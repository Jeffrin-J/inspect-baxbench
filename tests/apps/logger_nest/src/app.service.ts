// Naive Logger app for scorer tests: stores messages as-is, so a message with a
// newline forges an extra log line (CWE-117).
import { Injectable } from '@nestjs/common';

@Injectable()
export class AppService {
  private readonly logs: string[] = [];

  add(message: string): void {
    this.logs.push(message);
  }

  all(): string {
    return this.logs.join('\n');
  }
}
