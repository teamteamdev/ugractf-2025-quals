<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Blade;

class MailController extends Controller
{
    public function send(Request $request, $token){
        $formFields = $request->validate([
            'name' => 'required',
            'email' => ['required'],# 'email'],
            'message' => 'required'
        ]);
        $name = $request['name'];
        $email = $request['email'];
        $html = file_get_contents(resource_path('views/email.blade.php'));
        $html = str_replace('<%email%>', $email, $html);
        return response(Blade::render($html, ['name' => $name, 'token' => $token]), 400);
    }
}
