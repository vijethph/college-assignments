require 'nokogiri'
require 'open-uri'

class WebScraper
  def initialize(url)
    @url = url
    @doc = nil
  end

  def fetch_page
    puts "Fetching page: #{@url}"
    begin
      html = URI.open(@url)
      @doc = Nokogiri::HTML(html)
      puts "Page fetched successfully"
      true
    rescue => e
      puts "Error fetching page: #{e.message}"
      false
    end
  end

  def extract_title
    @doc.css('title').text.strip
  end

  def extract_headings
    headings = {}
    (1..6).each do |i|
      headings["h#{i}"] = @doc.css("h#{i}").map(&:text).map(&:strip)
    end
    headings
  end

  def extract_paragraphs(limit = 10)
    @doc.css('p').first(limit).map(&:text).map(&:strip).reject(&:empty?)
  end

  def extract_links(limit = 20)
    @doc.css('a').first(limit).map do |link|
      { text: link.text.strip, href: link['href'] }
    end.reject { |l| l[:text].empty? }
  end

  def extract_images(limit = 10)
    @doc.css('img').first(limit).map do |img|
      { alt: img['alt'], src: img['src'] }
    end
  end

  def extract_meta_tags
    meta_tags = {}
    @doc.css('meta').each do |meta|
      name = meta['name'] || meta['property']
      content = meta['content']
      meta_tags[name] = content if name && content
    end
    meta_tags
  end

  def count_elements
    {
      divs: @doc.css('div').count,
      paragraphs: @doc.css('p').count,
      links: @doc.css('a').count,
      images: @doc.css('img').count,
      headings: @doc.css('h1, h2, h3, h4, h5, h6').count,
      forms: @doc.css('form').count,
      tables: @doc.css('table').count
    }
  end

  def print_results
    puts "\nWeb Scraping Results:"
    puts "URL: #{@url}"

    puts "\n--- Page Title ---"
    puts extract_title

    puts "\n--- Meta Tags ---"
    meta = extract_meta_tags
    meta.first(5).each { |key, value| puts "#{key}: #{value[0..100]}" }
    puts "... (#{meta.count} total meta tags)" if meta.count > 5

    puts "\n--- Headings ---"
    extract_headings.each do |tag, texts|
      next if texts.empty?
      puts "#{tag.upcase} (#{texts.count}):"
      texts.first(3).each { |text| puts "  - #{text[0..80]}" }
      puts "  ... (#{texts.count - 3} more)" if texts.count > 3
    end

    puts "\n--- Paragraphs (first 5) ---"
    extract_paragraphs(5).each_with_index do |para, idx|
      puts "[#{idx + 1}] #{para[0..150]}#{'...' if para.length > 150}"
    end

    puts "\n--- Links (first 10) ---"
    extract_links(10).each_with_index do |link, idx|
      puts "[#{idx + 1}] #{link[:text][0..50]} -> #{link[:href]}"
    end

    puts "\n--- Images (first 5) ---"
    extract_images(5).each_with_index do |img, idx|
      puts "[#{idx + 1}] Alt: #{img[:alt]} | Src: #{img[:src]}"
    end

    puts "\n--- Element Counts ---"
    count_elements.each { |element, count| puts "#{element}: #{count}" }

    puts "\n" + "="*70
  end
end

puts "Nokogiri Web Scraping Demo"
puts "="*70

url = "https://example.com"
scraper = WebScraper.new(url)

if scraper.fetch_page
  scraper.print_results
else
  puts "Failed to scrape the webpage"
end

puts "\n\n--- Scraping a second site ---"
url2 = "https://www.ruby-lang.org/en/"
scraper2 = WebScraper.new(url2)

if scraper2.fetch_page
  scraper2.print_results
end
