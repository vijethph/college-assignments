class Book
  attr_accessor :title, :author, :unique_id, :isbn, :genre, :publication_year, :is_borrowed, :borrowed_by, :due_date

  def initialize(title, author, unique_id, isbn, genre, publication_year)
    @title = title
    @author = author
    @unique_id = unique_id
    @isbn = isbn
    @genre = genre
    @publication_year = publication_year
    @is_borrowed = false
    @borrowed_by = nil
    @due_date = nil
  end

  def borrow(user_id, due_date)
    @is_borrowed = true
    @borrowed_by = user_id
    @due_date = due_date
  end

  def return_book
    @is_borrowed = false
    @borrowed_by = nil
    @due_date = nil
  end

  def to_s
    status = @is_borrowed ? "Borrowed by User ID: #{@borrowed_by} (Due: #{@due_date})" : "Available"
    "Book ID: #{@unique_id} | Title: #{@title} | Author: #{@author} | Genre: #{@genre} | Status: #{status}"
  end
end