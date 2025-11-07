class EmailSpamDetector
  attr_reader :emails, :spam_keywords, :urgent_keywords, :money_keywords, :suspicious_patterns

  def initialize
    @spam_keywords = [
      "congratulations", "winner", "claim", "prize", "lottery", "inheritance",
      "million", "billion", "urgent", "act now", "limited time", "click here",
      "verify", "account", "suspended", "confirm", "password", "bank",
      "transfer", "beneficiary", "fund", "diplomat", "consignment"
    ]

    @urgent_keywords = ["urgent", "immediately", "act now", "expires", "deadline"]
    @money_keywords = ["million", "billion", "dollars", "usd", "funds", "transfer", "payment"]
    @suspicious_patterns = [/\d+\s*(million|billion)/, /usd\s*\$?\d+/i, /\d{3}-\d{3}-\d{4}/]

    @emails = []
  end

  def add_email(subject, content, is_spam)
    @emails << {
      subject: subject,
      content: content,
      is_spam: is_spam,
      words: (subject + " " + content).downcase.split(/\W+/)
    }
  end

  def calculate_spam_score(email)
    words = email[:words]
    content = email[:content].downcase
    score = 0

    spam_count = words.count { |word| @spam_keywords.include?(word) }
    score += spam_count * 1.5

    urgent_count = words.count { |word| @urgent_keywords.include?(word) }
    score += urgent_count * 2

    money_count = words.count { |word| @money_keywords.include?(word) }
    score += money_count * 1.5

    @suspicious_patterns.each do |pattern|
      score += 2 if content =~ pattern
    end

    score += 1 if content.include?("dear sir") || content.include?("dear friend")
    score += 1.5 if words.include?("nigeria") || words.include?("african")
    score += 1 if content =~ /\d+%/
    score += 0.5 if content.count("!") > 3

    [score, 10].min
  end

  def classify_email(email)
    score = calculate_spam_score(email)
    email[:spam_score] = score
    email[:classified_as_spam] = score >= 5
    email
  end

  def analyze_all
    @emails.each { |email| classify_email(email) }
  end

  def print_results
    puts "\nEmail Spam Detection Results"
    puts "="*70

    @emails.each_with_index do |email, idx|
      puts "\nEmail ##{idx + 1}: #{email[:subject]}"
      puts "-"*70
      puts "Actual: #{email[:is_spam] ? 'SPAM' : 'LEGITIMATE'}"
      puts "Classified as: #{email[:classified_as_spam] ? 'SPAM' : 'LEGITIMATE'}"
      puts "Spam Score: #{email[:spam_score].round(1)}/10"
      correct = email[:is_spam] == email[:classified_as_spam]
      puts "Result: #{correct ? 'CORRECT' : 'INCORRECT'}"
    end

    correct_count = @emails.count { |e| e[:is_spam] == e[:classified_as_spam] }
    accuracy = (correct_count.to_f / @emails.length * 100).round(1)

    puts "--- Accuracy: #{correct_count}/#{@emails.length} (#{accuracy}%) ---"
  end
end

detector = EmailSpamDetector.new

detector.add_email(
  "Meeting Tomorrow at 3pm",
  "Hi team, just a reminder that we have our weekly meeting tomorrow at 3pm. Please review the agenda and come prepared with your updates. See you there! Best regards, John",
  false
)

detector.add_email(
  "Your Amazon Order #12345",
  "Your order has been shipped and will arrive by Thursday. Track your package using the link in your account. Thank you for shopping with us. Customer Service Team",
  false
)

detector.add_email(
  "Quarterly Review Notes",
  "Attached are the notes from our quarterly review meeting. Please review the action items and let me know if you have any questions. We made good progress this quarter. Thanks, Sarah",
  false
)

detector.add_email(
  "Weekend Plans",
  "Hey, want to grab coffee this weekend? I found a new place downtown that looks great. Let me know what time works for you. Looking forward to catching up! Alex",
  false
)

detector.add_email(
  "Project Update - Phase 2",
  "The second phase of our project is now complete. All deliverables have been submitted and approved by the client. Great work everyone! Next meeting is scheduled for Monday. Regards, Project Manager",
  false
)

detector.add_email(
  "URGENT: Claim Your Prize Now!!!",
  "Dear Lucky Winner, Congratulations! You have won $5 million USD in our international lottery. To claim your prize, please send your bank account details immediately. This is a limited time offer. Act now before it expires! Contact our diplomat agent at 555-123-4567. Regards, Lottery Committee",
  true
)

detector.add_email(
  "Inheritance Fund Transfer - URGENT",
  "Dear Friend, I am a banker from Nigeria and I have urgent business proposal for you. My client died and left $25 million USD with no beneficiary. I need your help to transfer these funds. You will receive 40% as your share. Please respond immediately with your details. This is completely legal and risk-free. Best regards, Mr. Johnson",
  true
)

detector.add_email(
  "Your Account Has Been Suspended",
  "Dear Sir, Your bank account has been suspended due to suspicious activity. To verify your identity and reactivate your account, click here immediately and confirm your password and account details. Failure to act within 24 hours will result in permanent suspension. Urgent action required! Customer Service",
  true
)

detector.add_email(
  "Congratulations - You've Been Selected!",
  "Dear Winner, You have been selected to receive an inheritance of $10 million USD from a deceased diplomat. To claim this fund, send your personal information including bank account number immediately. This is a limited time opportunity. Act now! Contact us at the phone number 555-999-8888. Beneficiary Services",
  true
)

detector.add_email(
  "CLAIM YOUR FUNDS NOW - URGENT!!!",
  "Dear Friend, I am contacting you regarding a consignment box containing $15 million USD that needs to be transferred. You have been chosen as the beneficiary. Send your details urgently to claim your payment. This expires in 48 hours! Contact our African diplomat immediately. 100% legitimate and guaranteed! Wire Transfer Department",
  true
)

detector.analyze_all
detector.print_results
