source "https://rubygems.org"

gem "jekyll", "~> 4.3.2"
gem "jekyll-remote-theme"
gem 'jekyll-toc'
gem 'jekyll-seo'
gem 'jekyll-seo-tag'

# gem "github-pages", group: :jekyll_plugins
# plugins
group :jekyll_plugins do
  gem "jekyll-feed", "~> 0.12"
end

platforms :mingw, :x64_mingw, :mswin, :jruby do
  gem "tzinfo", ">= 1", "< 3"
  gem "tzinfo-data"
end

# Performance-booster for watching directories on Windows
gem "wdm", "~> 0.1.1", :platforms => [:mingw, :x64_mingw, :mswin]

# Lock `http_parser.rb` gem to `v0.6.x` on JRuby builds since newer versions of the gem
# do not have a Java counterpart.
gem "http_parser.rb", "~> 0.6.0", :platforms => [:jruby]

# fixes for 'Kernel.require': cannot load such file -- 
gem 'csv'
gem 'base64'