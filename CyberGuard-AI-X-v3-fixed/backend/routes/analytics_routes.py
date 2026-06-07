"""
CyberGuard AI X - Analytics Routes
Charts, trends, and statistics APIs
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.db import execute_query

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/category-distribution', methods=['GET'])
@jwt_required()
def category_distribution():
    data = execute_query(
        """SELECT category, COUNT(*) as count
           FROM complaints
           WHERE category IS NOT NULL
           GROUP BY category
           ORDER BY count DESC""",
        fetchall=True
    )
    return jsonify({'data': data or []})


@analytics_bp.route('/severity-distribution', methods=['GET'])
@jwt_required()
def severity_distribution():
    data = execute_query(
        """SELECT severity, COUNT(*) as count
           FROM complaints
           GROUP BY severity
           ORDER BY FIELD(severity, 'High', 'Medium', 'Low')""",
        fetchall=True
    )
    return jsonify({'data': data or []})


@analytics_bp.route('/monthly-trends', methods=['GET'])
@jwt_required()
def monthly_trends():
    data = execute_query(
        """SELECT
               DATE_FORMAT(created_at, '%Y-%m') as month,
               COUNT(*) as count,
               SUM(CASE WHEN severity = 'High' THEN 1 ELSE 0 END) as high_count,
               SUM(CASE WHEN severity = 'Medium' THEN 1 ELSE 0 END) as medium_count
           FROM complaints
           WHERE created_at >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
           GROUP BY DATE_FORMAT(created_at, '%Y-%m')
           ORDER BY month ASC""",
        fetchall=True
    )
    return jsonify({'data': data or []})


@analytics_bp.route('/department-distribution', methods=['GET'])
@jwt_required()
def department_distribution():
    data = execute_query(
        """SELECT department, COUNT(*) as count
           FROM complaints
           WHERE department IS NOT NULL
           GROUP BY department
           ORDER BY count DESC""",
        fetchall=True
    )
    return jsonify({'data': data or []})


@analytics_bp.route('/language-distribution', methods=['GET'])
@jwt_required()
def language_distribution():
    data = execute_query(
        """SELECT
               CASE
                   WHEN language = 'en' THEN 'English'
                   WHEN language = 'hi' THEN 'Hindi'
                   WHEN language = 'gu' THEN 'Gujarati'
                   ELSE 'Other'
               END as language_name,
               COUNT(*) as count
           FROM complaints
           GROUP BY language
           ORDER BY count DESC""",
        fetchall=True
    )
    return jsonify({'data': data or []})


@analytics_bp.route('/status-distribution', methods=['GET'])
@jwt_required()
def status_distribution():
    data = execute_query(
        """SELECT status, COUNT(*) as count
           FROM complaints
           GROUP BY status""",
        fetchall=True
    )
    return jsonify({'data': data or []})


@analytics_bp.route('/daily-complaints', methods=['GET'])
@jwt_required()
def daily_complaints():
    """Last 30 days daily complaint counts"""
    data = execute_query(
        """SELECT
               DATE(created_at) as date,
               COUNT(*) as count
           FROM complaints
           WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
           GROUP BY DATE(created_at)
           ORDER BY date ASC""",
        fetchall=True
    )
    return jsonify({'data': data or []})


@analytics_bp.route('/overview', methods=['GET'])
@jwt_required()
def overview():
    """Complete analytics overview for dashboard"""
    total = execute_query("SELECT COUNT(*) as c FROM complaints", fetchone=True)
    high_sev = execute_query("SELECT COUNT(*) as c FROM complaints WHERE severity = 'High'", fetchone=True)
    fraud = execute_query("SELECT COUNT(*) as c FROM complaints WHERE category IN ('Financial Fraud', 'Online Fraud')", fetchone=True)
    active_users = execute_query("SELECT COUNT(DISTINCT user_id) as c FROM complaints", fetchone=True)
    resolved = execute_query("SELECT COUNT(*) as c FROM complaints WHERE status = 'Resolved'", fetchone=True)
    pending = execute_query("SELECT COUNT(*) as c FROM complaints WHERE status = 'Pending'", fetchone=True)
    today = execute_query("SELECT COUNT(*) as c FROM complaints WHERE DATE(created_at) = CURDATE()", fetchone=True)

    # Recent complaints
    recent = execute_query(
        """SELECT c.id, c.category, c.severity, c.status, c.created_at, u.name as user_name
           FROM complaints c JOIN users u ON c.user_id = u.id
           ORDER BY c.created_at DESC LIMIT 5""",
        fetchall=True
    )

    return jsonify({
        'total_complaints': total['c'] if total else 0,
        'high_severity': high_sev['c'] if high_sev else 0,
        'fraud_cases': fraud['c'] if fraud else 0,
        'active_users': active_users['c'] if active_users else 0,
        'resolved_cases': resolved['c'] if resolved else 0,
        'pending_cases': pending['c'] if pending else 0,
        'today_complaints': today['c'] if today else 0,
        'recent_complaints': recent or [],
    })
