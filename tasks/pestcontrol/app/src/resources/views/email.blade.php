<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ОШИБКА (BUG)</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }
        .email-container {
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .header {
            text-align: center;
            padding-bottom: 20px;
            border-bottom: 1px solid #dddddd;
        }
        .header h1 {
            margin: 0;
            font-size: 24px;
            color: #333333;
        }
        .content {
            padding: 20px 0;
            color: #555555;
            line-height: 1.6;
        }
        .footer {
            text-align: center;
            padding-top: 20px;
            border-top: 1px solid #dddddd;
            font-size: 14px;
            color: #888888;
        }
        .button {
            display: inline-block;
            padding: 10px 20px;
            margin: 20px 0;
            font-size: 16px;
            color: #ffffff;
            background-color: #007bff;
            border-radius: 5px;
            text-decoration: none;
        }
        .button:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>Упс...</h1>
            <img class="w-24" src="/{{$token}}/sad-bug-with-napsack-smaller.png"/>
        </div>

        <div class="content">
            <p>Уважаемый(-ая) {{$name}}!</p>
            <p>К сожалению, нам не удалось направить Вам электронное письмо по адресу <%email%>.</p>
            <p>Возможно, Вы указали неверный адрес. Если Вы считаете, что адрес верный, то, скорее всего, Вы плохо считаете. Наш сайт, ровно как наши средства и препараты, работает в 100% случаев!</p>

            <p>С уважением,<br>ГБУ СОС СЭС СУС</p>
        </div>

        <div class="footer">
            <p>&copy; {{ date('Y') }} ГБУ СОС СЭС СУС. Все права защищены</p>
            <p>Нужны санитары? ГБУ СОС СЭС СУС устранит ваши кошмары!</p>
        </div>
    </div>
</body>
</html>