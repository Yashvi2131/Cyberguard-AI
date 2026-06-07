"""
CyberGuard AI X - Complaint Routes
Submit, list, filter, and manage complaints
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'ml'))

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.db import execute_query

complaint_bp = Blueprint('complaints', __name__)


def get_predictor_safe():
    try:
        from predict import get_predictor
        return get_predictor()
    except Exception:
        return None


@complaint_bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_complaint():
    user_id = int(get_jwt_identity())  # cast to int — JWT stores as string, DB column is INT
    db_user = execute_query(
        "SELECT id, role FROM users WHERE id = %s", (user_id,), fetchone=True
    )
    if not db_user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    complaint_text = data.get('complaint_text', '').strip()
    language_hint = data.get('language', None)

    if not complaint_text or len(complaint_text) < 20:
        return jsonify({'error': 'Complaint text too short (minimum 20 characters)'}), 400

    # Run AI prediction
    predictor = get_predictor_safe()
    if predictor:
        result = predictor.predict(complaint_text, language_hint)
    else:
        result = {
            'translated_text': complaint_text,
            'language': language_hint or 'en',
            'category': 'Online Fraud',
            'confidence': 50.0,
            'severity': 'Low',
            'department': 'General Cyber Crime Cell',
        }

    # Save complaint
    complaint_id = execute_query(
        """INSERT INTO complaints
           (user_id, complaint_text, language, translated_text, category,
            confidence_score, severity, department, status)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Pending')""",
        (
            user_id,
            complaint_text,
            result.get('language', 'en'),
            result.get('translated_text', complaint_text),
            result.get('category', 'Online Fraud'),
            result.get('confidence', 50.0),
            result.get('severity', 'Low'),
            result.get('department', 'General Cyber Crime Cell'),
        ),
        commit=True
    )

    # Log severity
    if complaint_id:
        try:
            keywords = str(result.get('keywords_detected', []))
            execute_query(
                "INSERT INTO severity_logs (complaint_id, severity_level, keywords_detected) VALUES (%s, %s, %s)",
                (complaint_id, result.get('severity', 'Low'), keywords), commit=True
            )
        except Exception:
            pass

        # Update analytics count
        try:
            execute_query(
                """INSERT INTO analytics (category, count, last_updated)
                   VALUES (%s, 1, NOW())
                   ON DUPLICATE KEY UPDATE count = count + 1, last_updated = NOW()""",
                (result.get('category', 'Online Fraud'),), commit=True
            )
        except Exception:
            pass

    result['complaint_id'] = complaint_id
    result['status'] = 'Pending'
    return jsonify({
        'message': 'Complaint submitted successfully',
        'complaint_id': complaint_id,
        'prediction': result
    }), 201


@complaint_bp.route('/', methods=['GET'])
@jwt_required()
def get_complaints():
    user_id = int(get_jwt_identity())  # cast to int
    db_user = execute_query(
        "SELECT id, role FROM users WHERE id = %s", (user_id,), fetchone=True
    )
    if not db_user:
        return jsonify({'error': 'User not found'}), 404
    role = db_user.get('role', 'user')

    # Query params
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    category = request.args.get('category', '')
    severity = request.args.get('severity', '')
    status = request.args.get('status', '')
    search = request.args.get('search', '')
    offset = (page - 1) * per_page

    # Build WHERE clause
    where = []
    params = []

    if role != 'admin':
        where.append("c.user_id = %s")
        params.append(user_id)

    if category:
        where.append("c.category = %s")
        params.append(category)
    if severity:
        where.append("c.severity = %s")
        params.append(severity)
    if status:
        where.append("c.status = %s")
        params.append(status)
    if search:
        where.append("c.complaint_text LIKE %s")
        params.append(f'%{search}%')

    where_sql = "WHERE " + " AND ".join(where) if where else ""

    # Count total
    count_result = execute_query(
        f"SELECT COUNT(*) as total FROM complaints c {where_sql}",
        tuple(params), fetchone=True
    )
    total = count_result['total'] if count_result else 0

    # Get complaints
    complaints = execute_query(
        f"""SELECT c.*, u.name as user_name, u.email as user_email
            FROM complaints c
            JOIN users u ON c.user_id = u.id
            {where_sql}
            ORDER BY c.created_at DESC
            LIMIT %s OFFSET %s""",
        tuple(params) + (per_page, offset), fetchall=True
    )

    return jsonify({
        'complaints': complaints or [],
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    })


@complaint_bp.route('/<int:complaint_id>', methods=['GET'])
@jwt_required()
def get_complaint(complaint_id):
    user_id = int(get_jwt_identity())  # cast to int
    db_user = execute_query(
        "SELECT id, role FROM users WHERE id = %s", (user_id,), fetchone=True
    )
    if not db_user:
        return jsonify({'error': 'User not found'}), 404
    role = db_user.get('role', 'user')

    complaint = execute_query(
        """SELECT c.*, u.name as user_name, u.email as user_email
           FROM complaints c
           JOIN users u ON c.user_id = u.id
           WHERE c.id = %s""",
        (complaint_id,), fetchone=True
    )

    if not complaint:
        return jsonify({'error': 'Complaint not found'}), 404

    # Both are now int — safe comparison
    if role != 'admin' and int(complaint['user_id']) != user_id:
        return jsonify({'error': 'Access denied'}), 403

    # Get severity log
    sev_log = execute_query(
        "SELECT * FROM severity_logs WHERE complaint_id = %s ORDER BY timestamp DESC LIMIT 1",
        (complaint_id,), fetchone=True
    )
    complaint['severity_log'] = sev_log

    return jsonify({'complaint': complaint})


@complaint_bp.route('/<int:complaint_id>/status', methods=['PUT'])
@jwt_required()
def update_status(complaint_id):
    user_id = int(get_jwt_identity())
    db_user = execute_query(
        "SELECT role FROM users WHERE id = %s", (user_id,), fetchone=True
    )
    if not db_user or db_user.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    data = request.get_json()
    new_status = data.get('status')
    valid_statuses = ['Pending', 'Under Review', 'Resolved', 'Closed']
    if new_status not in valid_statuses:
        return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400

    execute_query(
        "UPDATE complaints SET status = %s WHERE id = %s",
        (new_status, complaint_id), commit=True
    )
    return jsonify({'message': 'Status updated', 'status': new_status})


@complaint_bp.route('/stats/summary', methods=['GET'])
@jwt_required()
def get_summary_stats():
    user_id = int(get_jwt_identity())  # cast to int
    db_user = execute_query(
        "SELECT id, role FROM users WHERE id = %s", (user_id,), fetchone=True
    )
    if not db_user:
        return jsonify({'error': 'User not found'}), 404
    role = db_user.get('role', 'user')

    where = "" if role == 'admin' else f"WHERE user_id = {db_user['id']}"

    total = execute_query(f"SELECT COUNT(*) as c FROM complaints {where}", fetchone=True)
    high = execute_query(f"SELECT COUNT(*) as c FROM complaints {where} {'AND' if where else 'WHERE'} severity = 'High'" if where else "SELECT COUNT(*) as c FROM complaints WHERE severity = 'High'", fetchone=True)
    fraud = execute_query(f"SELECT COUNT(*) as c FROM complaints WHERE category = 'Financial Fraud'" + (" AND user_id = %s" if role != 'admin' else ""), (db_user['id'],) if role != 'admin' else None, fetchone=True)
    pending = execute_query(f"SELECT COUNT(*) as c FROM complaints WHERE status = 'Pending'" + (" AND user_id = %s" if role != 'admin' else ""), (db_user['id'],) if role != 'admin' else None, fetchone=True)

    return jsonify({
        'total_complaints': total['c'] if total else 0,
        'high_severity': high['c'] if high else 0,
        'fraud_cases': fraud['c'] if fraud else 0,
        'pending_cases': pending['c'] if pending else 0,
    })
