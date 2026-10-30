<?php

// Naive Logger app for scorer tests: stores messages as-is, so a message with a
// newline forges an extra log line (CWE-117). PHP's built-in server keeps no
// state between requests, so logs go to a file.

/** @var \Laravel\Lumen\Routing\Router $router */

use Illuminate\Http\Request;

$router->post('/log', function (Request $request) {
    $message = (string) $request->input('message', '');
    file_put_contents(storage_path('app_logs.txt'), $message . "\n", FILE_APPEND | LOCK_EX);
    return response('', 200);
});

$router->get('/logs', function () {
    $path = storage_path('app_logs.txt');
    $content = file_exists($path) ? file_get_contents($path) : '';
    return response($content, 200)->header('Content-Type', 'text/plain');
});
