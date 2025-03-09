<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>ГБУ СОС СЭС СУС</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="#">ГБУ СОС СЭС СУС</a>
        </div>
    </nav>

    <div class="container mt-5">
        <div class="row">
            <div class="col-lg-12 text-center">
                <h1>Нужны санитары?</h1>
                <p class="lead">Тогда мы идём к вам!</p>
            </div>
        </div>
        <div class="row">
            <div class="col-lg-6">
                <h2>Проводим все виды санитарных работ</h1>
                <p>Государственное бюджетное учреждение «Санитарно-оздоровительная Служба «Специализированная эпидемиологическая структура «Стопроцентное уничтожение существ» — это команда профессионалов, которая помогает создать безопасную и чистую среду для жизни и работы. Мы специализируемся на уничтожении вредоносных микроорганизмов, насекомых и грызунов, используя современные технологии и безопасные для здоровья средства.</p>
                <p><b>Оказываем услуги следующие и не только:</b></p>
                <ul>
                    <li>Дезинфекция помещений</li>
                    <li>Уничтожение насекомых (дезинсекция)</li>
                    <li>Борьба с грызунами (дератизация)</li>
                    <li>Очистка текстовых строк (деквотизация)</li>
                    <li>... и многое другое!</li>
                </ul>
                <p>Для получения первичной консультации от наших специалистов, воспользуйтесь ФОРМОЙ (внизу)</p>
            </div>
            <div class="col-lg-6">
                <h2 class="text-center mb-4">Связаться с нами</h2>
                <form action="/{{$token}}/svyazatsa-s-nami" method="POST">            
                    @csrf
                    <div class="mb-3">
                        <label for="name" class="form-label">Как к вам обращаться?</label>
                        <input type="text" class="form-control" id="name" name="name" required>
                    </div>
                    <div class="mb-3">
                        <label for="email" class="form-label">Ваш адрес электронной почты</label>
                        <input type="email" class="form-control" id="email" name="email" required>
                    </div>
                    <div class="mb-3">
                        <label for="message" class="form-label">Дополнительная информация</label>
                        <textarea class="form-control" id="message" name="message" rows="5" required></textarea>
                    </div>
                    <div class="d-grid">
                        <button type="submit" class="btn btn-primary">Отправить заявку!</button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <footer class="bg-dark text-white text-center py-3 fixed-bottom">
        <div class="container">
            <p class="mb-0">&copy; {{ date('Y') }} ГБУ СОС СЭС СУС. Все права защищены.</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>