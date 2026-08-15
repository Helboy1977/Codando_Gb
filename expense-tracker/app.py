from datetime import date

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

CATEGORIES = [
    "Alimentação",
    "Transporte",
    "Moradia",
    "Lazer",
    "Saúde",
    "Educação",
    "Outros",
]


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(40), nullable=False)
    expense_date = db.Column(db.Date, nullable=False, default=date.today)

    def to_dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "amount": self.amount,
            "category": self.category,
            "date": self.expense_date.isoformat(),
        }


def create_app(db_uri="sqlite:///expenses.db"):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.get("/")
    def index():
        return render_template("index.html", categories=CATEGORIES)

    @app.get("/api/expenses")
    def list_expenses():
        expenses = Expense.query.order_by(Expense.expense_date.desc(), Expense.id.desc()).all()
        return jsonify([e.to_dict() for e in expenses])

    @app.post("/api/expenses")
    def create_expense():
        data = request.get_json(silent=True) or {}

        description = (data.get("description") or "").strip()
        category = (data.get("category") or "").strip()
        amount_raw = data.get("amount")
        date_raw = (data.get("date") or "").strip()

        if not description:
            return jsonify({"error": "Descrição é obrigatória"}), 400
        if category not in CATEGORIES:
            return jsonify({"error": "Categoria inválida"}), 400
        try:
            amount = float(amount_raw)
        except (TypeError, ValueError):
            return jsonify({"error": "Valor inválido"}), 400
        if amount <= 0:
            return jsonify({"error": "Valor deve ser maior que zero"}), 400

        try:
            expense_date = date.fromisoformat(date_raw) if date_raw else date.today()
        except ValueError:
            return jsonify({"error": "Data inválida"}), 400

        expense = Expense(
            description=description,
            amount=amount,
            category=category,
            expense_date=expense_date,
        )
        db.session.add(expense)
        db.session.commit()
        return jsonify(expense.to_dict()), 201

    @app.delete("/api/expenses/<int:expense_id>")
    def delete_expense(expense_id):
        expense = db.session.get(Expense, expense_id)
        if expense is None:
            return jsonify({"error": "Gasto não encontrado"}), 404
        db.session.delete(expense)
        db.session.commit()
        return "", 204

    @app.get("/api/summary")
    def summary():
        expenses = Expense.query.all()
        by_category = {}
        total = 0.0
        for e in expenses:
            by_category[e.category] = by_category.get(e.category, 0.0) + e.amount
            total += e.amount
        return jsonify({"total": total, "by_category": by_category})

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
