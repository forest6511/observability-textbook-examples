// Go は手動 SDK 計装が正直なベースライン。
// TracerProvider を作って OTLP で Collector に送り、HTTP ハンドラを
// otelhttp でラップして span 化する。さらに手動 span を 1 つ足す。
package main

import (
	"context"
	"log"
	"math/rand"
	"net/http"
	"os"
	"time"

	"go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.26.0"
)

func initTracer(ctx context.Context) (*sdktrace.TracerProvider, error) {
	// OTLP gRPC で Collector（otel-collector:4317）に送る exporter。
	exporter, err := otlptracegrpc.New(ctx,
		otlptracegrpc.WithEndpoint(os.Getenv("OTEL_EXPORTER_OTLP_ENDPOINT")),
		otlptracegrpc.WithInsecure(),
	)
	if err != nil {
		return nil, err
	}
	// service.name を付けておくと Tempo でサービス単位に見える。
	res, err := resource.New(ctx,
		resource.WithAttributes(semconv.ServiceName("go-dice")),
	)
	if err != nil {
		return nil, err
	}
	tp := sdktrace.NewTracerProvider(
		sdktrace.WithBatcher(exporter),
		sdktrace.WithResource(res),
	)
	otel.SetTracerProvider(tp)
	return tp, nil
}

func rollHandler(w http.ResponseWriter, r *http.Request) {
	// 自動計装（otelhttp）の span の下に手動 span をぶら下げる。
	tracer := otel.Tracer("dice.app")
	_, span := tracer.Start(r.Context(), "charge")
	defer span.End()

	value := rand.Intn(6) + 1
	span.SetAttributes(attribute.Int("dice.value", value))
	w.Write([]byte("value=" + string(rune('0'+value)) + "\n"))
}

func main() {
	ctx := context.Background()
	tp, err := initTracer(ctx)
	if err != nil {
		log.Fatal(err)
	}
	defer func() {
		_ = tp.Shutdown(context.Background())
	}()

	// otelhttp.NewHandler で HTTP ハンドラを自動計装する。
	handler := otelhttp.NewHandler(http.HandlerFunc(rollHandler), "roll")
	http.Handle("/roll", handler)

	srv := &http.Server{Addr: ":8001", ReadTimeout: 5 * time.Second}
	log.Println("go-dice listening on :8001")
	log.Fatal(srv.ListenAndServe())
}
