from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from models.member import Member
from config import Config

members_bp = Blueprint('members', __name__)

@members_bp.route('/')
def list_members():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    per_page = Config.ITEMS_PER_PAGE
    skip = (page - 1) * per_page
    
    members, total = Member.get_all(skip, per_page, search)
    
    return render_template('members.html', 
                         members=members, 
                         total=total, 
                         page=page,
                         per_page=per_page,
                         search=search)

@members_bp.route('/add', methods=['POST'])
def add_member():
    try:
        member_data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'address': request.form.get('address'),
            'member_type': request.form.get('member_type', 'Regular'),
            'max_books': int(request.form.get('max_books', 5))
        }
        
        # Check if email already exists
        existing = Member.find_by_email(member_data['email'])
        if existing:
            return jsonify({'success': False, 'message': 'Email already registered'}), 400
        
        member_id, member_number = Member.create(member_data)
        return jsonify({'success': True, 'message': f'Member added successfully. Member ID: {member_number}', 'member_id': str(member_id)})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@members_bp.route('/edit/<member_id>', methods=['GET', 'POST'])
def edit_member(member_id):
    if request.method == 'POST':
        try:
            update_data = {
                'name': request.form.get('name'),
                'phone': request.form.get('phone'),
                'address': request.form.get('address'),
                'member_type': request.form.get('member_type'),
                'max_books': int(request.form.get('max_books')),
                'membership_status': request.form.get('membership_status')
            }
            
            Member.update(member_id, update_data)
            return jsonify({'success': True, 'message': 'Member updated successfully'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    member = Member.find_by_id(member_id)
    if not member:
        flash('Member not found', 'error')
        return redirect(url_for('members.list_members'))
    
    return render_template('edit_member.html', member=member)

@members_bp.route('/delete/<member_id>', methods=['POST'])
def delete_member(member_id):
    try:
        success, message = Member.delete(member_id)
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@members_bp.route('/get/<member_id>')
def get_member(member_id):
    member = Member.find_by_id(member_id)
    if member:
        member['_id'] = str(member['_id'])
        return jsonify({'success': True, 'member': member})
    return jsonify({'success': False, 'message': 'Member not found'}), 404