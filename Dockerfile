FROM ruby:3.4.4-bookworm

RUN gem install jekyll bundler

RUN mkdir /app

COPY Gemfile* /app

WORKDIR /app

RUN bundle install

COPY . /app

EXPOSE 4000

CMD ["sh", "-c", "bundle exec jekyll serve --host 0.0.0.0 --destination /tmp/www --livereload"]