package main

import (
	"context"
	"encoding/json"
	"errors"
	"os"
	"testing"
)

type modelFunc func(context.Context, Request) (Response, error)

func (f modelFunc) Generate(ctx context.Context, r Request) (Response, error) { return f(ctx, r) }
func inputFixture(t *testing.T) AlertInput {
	t.Helper()
	data, err := os.ReadFile("fixtures/alert.json")
	if err != nil {
		t.Fatal(err)
	}
	var in AlertInput
	if err := json.Unmarshal(data, &in); err != nil {
		t.Fatal(err)
	}
	return in
}
func reportFixture(t *testing.T) Report {
	t.Helper()
	data, err := os.ReadFile("fixtures/report.json")
	if err != nil {
		t.Fatal(err)
	}
	var report Report
	if err := json.Unmarshal(data, &report); err != nil {
		t.Fatal(err)
	}
	return report
}
func TestEvidenceGateBeforeModelCall(t *testing.T) {
	for _, tc := range []struct {
		name, status string
		mutate       func(*AlertInput)
	}{
		{"no evidence", "needs_review", func(in *AlertInput) { in.Evidence = []Evidence{} }},
		{"duplicate ID", "invalid_input", func(in *AlertInput) { in.Evidence[1].ID = in.Evidence[0].ID }},
		{"reversed window", "invalid_input", func(in *AlertInput) { in.WindowEnd = in.WindowStart }},
	} {
		t.Run(tc.name, func(t *testing.T) {
			in := inputFixture(t)
			tc.mutate(&in)
			model := modelFunc(func(context.Context, Request) (Response, error) {
				t.Fatal("must not call model")
				return Response{}, nil
			})
			got := Analyze(context.Background(), model, in)
			if got.Status != tc.status || got.Report != nil {
				t.Fatalf("unexpected result: %+v", got)
			}
		})
	}
}
func TestReportAcceptanceBoundary(t *testing.T) {
	for _, tc := range []struct {
		name, status string
		mutate       func(*Report)
	}{
		{"draft remains a draft", "draft", func(*Report) {}},
		{"unknown reference", "unavailable", func(r *Report) { r.Findings[0].EvidenceIDs = []string{"E999"} }},
		{"missing reference", "unavailable", func(r *Report) { r.Findings[0].EvidenceIDs = []string{} }},
		{"false success label", "unavailable", func(r *Report) { r.Assessment = "resolved" }},
		{"missing information", "needs_review", func(r *Report) { r.Assessment = "insufficient_data" }},
		{"unexplained uncertainty", "unavailable", func(r *Report) { r.Assessment = "insufficient_data"; r.OpenQuestions = []string{} }},
	} {
		t.Run(tc.name, func(t *testing.T) {
			report := reportFixture(t)
			tc.mutate(&report)
			body, err := json.Marshal(report)
			if err != nil {
				t.Fatal(err)
			}
			model := modelFunc(func(_ context.Context, r Request) (Response, error) {
				if r.PromptVersion != "alert-report-v1" || len(r.InputJSON) == 0 {
					t.Fatal("missing request contract")
				}
				return Response{Body: body, Finish: "complete"}, nil
			})
			got := Analyze(context.Background(), model, inputFixture(t))
			if got.Status != tc.status {
				t.Fatalf("unexpected result: %+v", got)
			}
			if tc.status == "unavailable" && got.Report != nil {
				t.Fatal("rejected output leaked as report")
			}
		})
	}
}
func TestFailedGenerationDoesNotProduceReport(t *testing.T) {
	for _, tc := range []struct {
		name     string
		response Response
		err      error
	}{
		{"timeout", Response{}, context.DeadlineExceeded},
		{"provider error", Response{}, errors.New("upstream error")},
		{"truncated", Response{Body: []byte(`{"assessment":"draft"}`), Finish: "truncated"}, nil},
		{"refusal", Response{Finish: "refused"}, nil},
		{"extra JSON", Response{Body: []byte(`{} {}`), Finish: "complete"}, nil},
		{"null", Response{Body: []byte(`null`), Finish: "complete"}, nil},
	} {
		t.Run(tc.name, func(t *testing.T) {
			got := Analyze(context.Background(), modelFunc(func(context.Context, Request) (Response, error) { return tc.response, tc.err }), inputFixture(t))
			if got.Status != "unavailable" || got.Report != nil {
				t.Fatalf("unexpected result: %+v", got)
			}
		})
	}
}
func TestCanceledRequestDoesNotCallModel(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	model := modelFunc(func(context.Context, Request) (Response, error) {
		t.Fatal("canceled request called model")
		return Response{}, nil
	})
	got := Analyze(ctx, model, inputFixture(t))
	if got.Status != "unavailable" || got.Report != nil {
		t.Fatalf("unexpected result: %+v", got)
	}
}
