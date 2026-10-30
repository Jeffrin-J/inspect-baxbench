import { Body, Controller, Get, Header, HttpCode, Post } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('log')
  @HttpCode(200)
  log(@Body() body: { message?: unknown }): void {
    this.appService.add(String(body?.message ?? ''));
  }

  @Get('logs')
  @Header('Content-Type', 'text/plain')
  logs(): string {
    return this.appService.all();
  }
}
