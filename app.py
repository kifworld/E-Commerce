import flet as ft
import requests

API = "http://127.0.0.1:8000"

def main(page: ft.Page):

    # ---------------- THEME ----------------
    page.title = "AI E-Commerce System"
    page.bgcolor = "#f3f4f6"
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    selected = []
    token = None

    # ---------------- UI STATE ----------------
    menu_box = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    order_box = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    ai_box = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    admin_review_box = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    username = ft.TextField(label="Admin Username", width=300)
    password = ft.TextField(label="Password", password=True, width=300)

    name_input = ft.TextField(label="Name", width=300)
    comment_input = ft.TextField(label="Comment", width=300)

    rating_dropdown = ft.Dropdown(
        width=300,
        label="Rating (1–5)",
        options=[
            ft.dropdown.Option("1"),
            ft.dropdown.Option("2"),
            ft.dropdown.Option("3"),
            ft.dropdown.Option("4"),
            ft.dropdown.Option("5"),
        ]
    )

    # ---------------- TITLE ----------------
    title = ft.Text(
        "🍔 AI E-Commerce System",
        size=30,
        weight="bold",
        color="#111827"
    )

    # ---------------- MENU ----------------
    def load_menu(e):
        res = requests.get(f"{API}/menu")
        data = res.json()

        menu_box.controls.clear()

        for item in data:
            def add(i=item):
                selected.append(i)
                page.snack_bar = ft.SnackBar(ft.Text(f"Added {i['name']}"))
                page.snack_bar.open = True
                page.update()

            menu_box.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(f"{item['name']} - ${item['price']}", color="#111827"),
                            ft.ElevatedButton("Add", on_click=lambda e, i=item: add(i))
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    padding=10,
                    width=400,
                    bgcolor="white",
                    border=ft.border.all(1, "#e5e7eb"),
                    border_radius=12
                )
            )

        page.update()

    # ---------------- ORDER ----------------
    def place_order(e):
        res = requests.post(f"{API}/order", json={"items": selected})
        data = res.json()["receipt"]

        order_box.controls.clear()
        order_box.controls.append(ft.Text("🧾 RECEIPT", size=20, color="#111827"))

        for i in data["items"]:
            order_box.controls.append(ft.Text(i["name"], color="#111827"))

        order_box.controls.append(ft.Text(f"Total: ${data['total']}", color="#111827"))
        order_box.controls.append(ft.Text(f"Ticket: {data['ticket']}", color="#111827"))

        selected.clear()
        page.update()

    # ---------------- LOGIN ----------------
    def login(e):
        nonlocal token

        res = requests.post(f"{API}/login", json={
            "username": username.value,
            "password": password.value
        })

        if res.status_code == 200:
            token = res.json()["token"]
            page.snack_bar = ft.SnackBar(ft.Text("Admin logged in"))
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Login failed"))

        page.snack_bar.open = True
        page.update()

    # ---------------- AI ----------------
    def ai_summary(e):
        res = requests.get(f"{API}/ai/summary")
        data = res.json()

        ai_box.controls.clear()
        ai_box.controls.append(ft.Text("📊 AI SUMMARY", size=20, color="#111827"))

        for k, v in data.items():
            ai_box.controls.append(ft.Text(f"{k}: {v}", color="#111827"))

        page.update()

    def ai_issues(e):
        res = requests.get(f"{API}/ai/issues")
        data = res.json()

        ai_box.controls.clear()
        ai_box.controls.append(ft.Text("⚠ AI ISSUES", size=20, color="#111827"))
        ai_box.controls.append(ft.Text(f"Status: {data['status']}", color="#111827"))

        for i in data["issues"]:
            ai_box.controls.append(ft.Text(f"- {i}", color="#111827"))

        page.update()

    # ---------------- REVIEW AI ----------------
    def analyze_review(rating, comment, total_price):
        rating = int(rating)
        text = (comment or "").lower()

        # sentiment base
        if rating <= 2:
            mood = "😡 Negative"
        elif rating == 3:
            mood = "😐 Neutral"
        else:
            mood = "😄 Positive"

        # AI-like keyword detection
        negative_words = ["bad", "worst", "slow", "late", "dirty", "cold", "expensive"]
        positive_words = ["good", "great", "amazing", "fast", "nice", "perfect", "cheap"]

        if any(w in text for w in negative_words):
            mood = "😡 Negative (AI detected)"
        elif any(w in text for w in positive_words):
            mood = "😄 Positive (AI detected)"

        # price context
        if total_price == 0:
            price_tag = "🧾 No order linked"
        elif total_price < 10:
            price_tag = "💸 Cheap experience"
        elif total_price < 25:
            price_tag = "💰 Normal experience"
        else:
            price_tag = "💎 Premium experience"

        return mood, price_tag

    # ---------------- SUBMIT REVIEW ----------------
    def submit_review(e):
        nonlocal selected

        total_price = sum(i["price"] for i in selected) if selected else 0

        mood, price_tag = analyze_review(
            rating_dropdown.value,
            comment_input.value,
            total_price
        )

        final_comment = f"{comment_input.value} | {mood} | {price_tag}"

        requests.post(f"{API}/review", json={
            "name": name_input.value,
            "rating": int(rating_dropdown.value),
            "comment": final_comment
        })

        page.snack_bar = ft.SnackBar(
            ft.Text(f"Review saved → {mood} | {price_tag}")
        )
        page.snack_bar.open = True
        page.update()

    # ---------------- LOAD REVIEWS ----------------
    def load_reviews(e):
        if not token:
            page.snack_bar = ft.SnackBar(ft.Text("Login first"))
            page.snack_bar.open = True
            page.update()
            return

        res = requests.get(
            f"{API}/reviews",
            headers={"Authorization": f"Bearer {token}"}
        )

        data = res.json()

        admin_review_box.controls.clear()
        admin_review_box.controls.append(ft.Text("⭐ REVIEWS", size=20, color="#111827"))

        for r in data:
            admin_review_box.controls.append(
                ft.Container(
                    content=ft.Text(
                        f"{r['name']} ({r['rating']}/5)\n{r['comment']}",
                        color="#111827"
                    ),
                    padding=10,
                    bgcolor="white",
                    border=ft.border.all(1, "#e5e7eb"),
                    border_radius=10,
                    width=300
                )
            )

        page.update()

    # ---------------- MAIN LAYOUT ----------------
    page.add(

        ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[

                title,
                ft.Divider(),

                # ---------------- CUSTOMER PLAYBOARD ----------------
                ft.Container(
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[

                            ft.Text("👤 Customer Playboard", size=22, color="#111827"),

                            ft.ElevatedButton("Load Menu", on_click=load_menu),
                            menu_box,

                            ft.ElevatedButton("Place Order", on_click=place_order),
                            order_box,

                            ft.Divider(),

                            ft.Text("⭐ Leave a Review", size=20, color="#111827"),

                            name_input,
                            rating_dropdown,
                            comment_input,

                            ft.ElevatedButton("Submit Review", on_click=submit_review),
                        ]
                    ),
                    padding=20,
                    bgcolor="white",
                    border=ft.border.all(1, "#e5e7eb"),
                    border_radius=12,
                    width=700
                ),

                ft.Divider(),

                # ---------------- LOWER DASHBOARD ----------------
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                    controls=[

                        # ADMIN PANEL
                        ft.Container(
                            content=ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[

                                    ft.Text("🔐 Admin Panel", size=20, color="#111827"),

                                    username,
                                    password,

                                    ft.ElevatedButton("Login", on_click=login),
                                    ft.ElevatedButton("AI Summary", on_click=ai_summary),
                                    ft.ElevatedButton("AI Issues", on_click=ai_issues),
                                    ft.ElevatedButton("Load Reviews", on_click=load_reviews),

                                    ai_box
                                ]
                            ),
                            padding=20,
                            bgcolor="white",
                            border=ft.border.all(1, "#e5e7eb"),
                            border_radius=12,
                            width=330
                        ),

                        # REVIEWS PANEL
                        ft.Container(
                            content=ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[

                                    ft.Text("⭐ Reviews Dashboard", size=20, color="#111827"),

                                    admin_review_box
                                ]
                            ),
                            padding=20,
                            bgcolor="white",
                            border=ft.border.all(1, "#e5e7eb"),
                            border_radius=12,
                            width=330
                        ),

                    ]
                )
            ]
        )
    )

ft.app(target=main)