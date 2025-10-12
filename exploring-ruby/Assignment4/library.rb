class Library
  attr_accessor :name, :books, :users, :borrowed_books, :available_books

  def initialize(name)
    @name = name
    @books = []
    @users = []
    @borrowed_books = []
    @available_books = []
  end

  def add_book(book)
    @books << book
    @available_books << book.unique_id
  end

  def add_user(user)
    @users << user
  end

  def find_book(book_id)
    @books.find { |book| book.unique_id == book_id }
  end

  def find_user(user_id)
    @users.find { |user| user.unique_id == user_id }
  end

  def borrow_book(user_id, book_id)
    user = find_user(user_id)
    book = find_book(book_id)

    if user.nil?
      puts "Error: User not found"
      return false
    end

    if book.nil?
      puts "Error: Book not found"
      return false
    end

    if book.is_borrowed
      puts "Error: Book is already borrowed"
      return false
    end

    unless user.can_borrow?
      puts "Error: User has reached borrowing limit"
      return false
    end

    due_date = (Time.now + (14 * 24 * 60 * 60)).strftime("%Y-%m-%d")
    book.borrow(user_id, due_date)
    user.borrow_book(book_id)
    @available_books.delete(book_id)
    @borrowed_books << book_id

    puts "Success: #{user.name} borrowed '#{book.title}'"
    true
  end

  def return_book(user_id, book_id)
    user = find_user(user_id)
    book = find_book(book_id)

    if user.nil? || book.nil?
      puts "Error: User or Book not found"
      return false
    end

    unless book.is_borrowed && book.borrowed_by == user_id
      puts "Error: This book is not borrowed by this user"
      return false
    end

    book.return_book
    user.return_book(book_id)
    @borrowed_books.delete(book_id)
    @available_books << book_id

    puts "Success: #{user.name} returned '#{book.title}'"
    true
  end

  def show_status
    puts "\n" + "=" * 60
    puts "LIBRARY: #{@name}"
    puts "=" * 60
    puts "Total Books: #{@books.length}"
    puts "Available Books: #{@available_books.length}"
    puts "Borrowed Books: #{@borrowed_books.length}"
    puts "Registered Users: #{@users.length}"
    puts "-" * 60
  end

  def show_all_books
    puts "\nALL BOOKS:"
    @books.each { |book| puts "  #{book}" }
  end

  def show_all_users
    puts "\nALL USERS:"
    @users.each { |user| puts "  #{user}" }
  end

  def search_books_by_genre(genre)
    puts "\nBooks in genre '#{genre}':"
    matching_books = @books.select { |book| book.genre.downcase == genre.downcase }
    if matching_books.empty?
      puts "  No books found in this genre"
    else
      matching_books.each { |book| puts "  #{book}" }
    end
  end
end
