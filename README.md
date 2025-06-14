## Development

## Docker

Start a build server inside a docker container without the hassle of software installation

```bash
# Build environment
docker build -t jekyll-www .
# Start server from a container
docker run -it --rm -v $PWD:/src -p 4000:4000 --name jekyll-www jekyll-www
```

### macOS

Use [ruby-install](https://github.com/postmodern/ruby-install) to manage ruby versions

```bash
brew install chruby ruby-install
```

Install a version of ruby

```bash
ruby-install ruby <version number>
```

Adding `ruby-install` startup script to [dotfiles](https://github.com/giahuy2201/dotfiles/blob/41f3cde2014f4bc517991f4c7a5bddf520852c70/common/.config/common/darwin.sh#L23)

Set ruby version

```bash
chruby <version number>
```

Install more

```bash
gem install jekyll bundler 
```

Install libraries

```bash
bundle install
```

Starting a server

```bash
bundle exec jekyll serve --livereload
```

## Reference

https://jekyllrb.com/docs/installation/macos/