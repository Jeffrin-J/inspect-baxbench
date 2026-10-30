Rails.application.routes.draw do
  post "/log", to: "logs#create"
  get "/logs", to: "logs#index"
end
