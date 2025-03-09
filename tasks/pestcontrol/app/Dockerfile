FROM php:8.3

RUN apt-get update -y && apt-get install -y openssl zip unzip git
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer

WORKDIR /app
COPY ./src/ /app

RUN composer install
RUN touch /app/database/database.sqlite && php artisan migrate --force && php artisan key:generate

ENTRYPOINT ["php", "artisan", "serve", "--host=0.0.0.0", "--quiet"]
