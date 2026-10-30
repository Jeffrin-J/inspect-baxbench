# Naive Logger app for scorer tests: stores messages as-is, so a message with a
# newline forges an extra log line (CWE-117).
class LogsController < ApplicationController
  LOG_FILE = Rails.root.join("tmp", "app_logs.txt")

  def create
    File.open(LOG_FILE, "a") { |f| f.puts(params[:message].to_s) }
    head :ok
  end

  def index
    render plain: File.exist?(LOG_FILE) ? File.read(LOG_FILE) : ""
  end
end
