<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\MailController;

Route::get('/{token}', function ($token) {
    return view('index', ['token' => $token]);
})->where('token', '[a-z0-9]{16}');

Route::post('/{token}/svyazatsa-s-nami', [MailController::class, 'send'])->where('token', '[a-z0-9]{16}');

Route::get('/{token}/sad-bug-with-napsack-smaller.png', function ($token) {
    $path = storage_path('/app/private/sad-bug-with-napsack-smaller.png');
    return response()->file($path);
})->where('token', '[a-z0-9]{16}');