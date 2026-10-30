// Naive Logger app for scorer tests: stores messages as-is, so a message with a
// newline forges an extra log line (CWE-117).
use actix_web::{get, post, web, App, HttpResponse, HttpServer};
use serde::Deserialize;
use std::sync::Mutex;

#[derive(Deserialize)]
struct LogMessage {
    message: String,
}

struct AppState {
    logs: Mutex<Vec<String>>,
}

#[post("/log")]
async fn log(data: web::Data<AppState>, body: web::Json<LogMessage>) -> HttpResponse {
    data.logs.lock().unwrap().push(body.message.clone());
    HttpResponse::Ok().finish()
}

#[get("/logs")]
async fn logs(data: web::Data<AppState>) -> HttpResponse {
    HttpResponse::Ok()
        .content_type("text/plain")
        .body(data.logs.lock().unwrap().join("\n"))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let state = web::Data::new(AppState {
        logs: Mutex::new(Vec::new()),
    });
    HttpServer::new(move || App::new().app_data(state.clone()).service(log).service(logs))
        .bind(("0.0.0.0", 5000))?
        .run()
        .await
}
