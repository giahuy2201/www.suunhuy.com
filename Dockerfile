FROM ruby:3.4.4-bookworm

RUN gem install jekyll bundler

COPY . /src

WORKDIR /src

RUN bundle install

EXPOSE 4000

CMD ["sh", "-c", "bundle exec jekyll serve --host 0.0.0.0 --destination /tmp/www--livereload"]