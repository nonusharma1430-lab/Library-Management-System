// Global functions for the library management system

$(document).ready(function() {
    // Add Book Form Submission
    $('#addBookForm').on('submit', function(e) {
        e.preventDefault();
        $.ajax({
            url: '/books/add',
            method: 'POST',
            data: $(this).serialize(),
            success: function(response) {
                if (response.success) {
                    showNotification('success', response.message);
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showNotification('danger', response.message);
                }
            },
            error: function(xhr) {
                showNotification('danger', xhr.responseJSON?.message || 'Error adding book');
            }
        });
    });
    
    // Add Member Form Submission
    $('#addMemberForm').on('submit', function(e) {
        e.preventDefault();
        $.ajax({
            url: '/members/add',
            method: 'POST',
            data: $(this).serialize(),
            success: function(response) {
                if (response.success) {
                    showNotification('success', response.message);
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showNotification('danger', response.message);
                }
            },
            error: function(xhr) {
                showNotification('danger', xhr.responseJSON?.message || 'Error adding member');
            }
        });
    });
    
    // Issue Book Form
    $('#issueBookForm').on('submit', function(e) {
        e.preventDefault();
        $.ajax({
            url: '/transactions/issue',
            method: 'POST',
            data: $(this).serialize(),
            success: function(response) {
                if (response.success) {
                    showNotification('success', response.message);
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showNotification('danger', response.message);
                }
            },
            error: function(xhr) {
                showNotification('danger', xhr.responseJSON?.message || 'Error issuing book');
            }
        });
    });
});

// Edit Book
function editBook(bookId) {
    $.get(`/books/get/${bookId}`, function(response) {
        if (response.success) {
            const book = response.book;
            $('#edit_book_id').val(bookId);
            $('#edit_title').val(book.title);
            $('#edit_author').val(book.author);
            $('#edit_publisher').val(book.publisher);
            $('#edit_year').val(book.year);
            $('#edit_category').val(book.category);
            $('#edit_total_copies').val(book.total_copies);
            $('#edit_location').val(book.location);
            $('#edit_description').val(book.description);
            $('#editBookModal').modal('show');
        }
    });
}

// Delete Book
function deleteBook(bookId) {
    if (confirm('Are you sure you want to delete this book?')) {
        $.ajax({
            url: `/books/delete/${bookId}`,
            method: 'POST',
            success: function(response) {
                if (response.success) {
                    showNotification('success', response.message);
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showNotification('danger', response.message);
                }
            }
        });
    }
}

// Edit Member
function editMember(memberId) {
    $.get(`/members/get/${memberId}`, function(response) {
        if (response.success) {
            const member = response.member;
            $('#edit_member_id').val(memberId);
            $('#edit_name').val(member.name);
            $('#edit_email').val(member.email);
            $('#edit_phone').val(member.phone);
            $('#edit_address').val(member.address);
            $('#edit_member_type').val(member.member_type);
            $('#edit_max_books').val(member.max_books);
            $('#edit_status').val(member.membership_status);
            $('#editMemberModal').modal('show');
        }
    });
}

// Delete Member
function deleteMember(memberId) {
    if (confirm('Are you sure you want to delete this member?')) {
        $.ajax({
            url: `/members/delete/${memberId}`,
            method: 'POST',
            success: function(response) {
                if (response.success) {
                    showNotification('success', response.message);
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showNotification('danger', response.message);
                }
            }
        });
    }
}

// Return Book
function returnBook(transactionId) {
    if (confirm('Confirm book return?')) {
        $.ajax({
            url: '/transactions/return',
            method: 'POST',
            data: { transaction_id: transactionId, fine_amount: 0 },
            success: function(response) {
                if (response.success) {
                    showNotification('success', response.message);
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showNotification('danger', response.message);
                }
            }
        });
    }
}

// Search Books for Issue
function searchBooks(query) {
    if (query.length < 2) return;
    $.get(`/transactions/search-book?q=${query}`, function(books) {
        const results = $('#bookSearchResults');
        results.empty();
        books.forEach(book => {
            results.append(`
                <div class="list-group-item list-group-item-action" onclick="selectBook('${book._id}', '${book.title}')">
                    <strong>${book.title}</strong><br>
                    <small>${book.author} - ${book.isbn} (${book.available_copies} available)</small>
                </div>
            `);
        });
        results.show();
    });
}

// Search Members for Issue
function searchMembers(query) {
    if (query.length < 2) return;
    $.get(`/transactions/search-member?q=${query}`, function(members) {
        const results = $('#memberSearchResults');
        results.empty();
        members.forEach(member => {
            results.append(`
                <div class="list-group-item list-group-item-action" onclick="selectMember('${member._id}', '${member.name}', '${member.member_id}')">
                    <strong>${member.name}</strong><br>
                    <small>${member.member_id} - ${member.email}</small>
                </div>
            `);
        });
        results.show();
    });
}

// Select Book
function selectBook(id, title) {
    $('#selectedBookId').val(id);
    $('#selectedBookName').text(title);
    $('#bookSearchInput').val(title);
    $('#bookSearchResults').hide();
}

// Select Member
function selectMember(id, name, memberId) {
    $('#selectedMemberId').val(id);
    $('#selectedMemberName').text(`${name} (${memberId})`);
    $('#memberSearchInput').val(name);
    $('#memberSearchResults').hide();
}

// Show Notification
function showNotification(type, message) {
    const toast = $(`
        <div class="toast align-items-center text-white bg-${type} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `);
    
    $('.toast-container').append(toast);
    const bsToast = new bootstrap.Toast(toast[0]);
    bsToast.show();
    
    toast.on('hidden.bs.toast', function() {
        $(this).remove();
    });
}

// Get Member Active Books
function getMemberBooks(memberId) {
    $.get(`/transactions/member-transactions/${memberId}`, function(response) {
        if (response.success) {
            const books = response.transactions;
            let html = '<h6>Currently Borrowed Books:</h6><ul>';
            books.forEach(book => {
                html += `<li>${book.book_title} - Due in ${book.days_left} days</li>`;
            });
            html += '</ul>';
            $('#memberBooksList').html(html);
        }
    });
}