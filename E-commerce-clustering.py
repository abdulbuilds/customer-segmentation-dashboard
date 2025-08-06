import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.cluster import KMeans
import numpy as np

class ECommerceDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("🧠 AI-Powered E-Commerce Sales Analyzer")
        self.root.geometry("950x750")
        self.root.config(bg="#f5f5f5")

        self.df = None

        title = tk.Label(self.root, text="E-Commerce Dashboard with AI Integration", font=("Helvetica", 18, "bold"), bg="#f5f5f5", fg="#333")
        title.pack(pady=15)

        # Entry Frame
        entry_frame = tk.Frame(self.root, bg="#f5f5f5")
        entry_frame.pack()

        tk.Label(entry_frame, text="Top N Products:", bg="#f5f5f5", font=("Arial", 12)).grid(row=0, column=0)
        self.entry_top_n = tk.Entry(entry_frame, width=5, font=("Arial", 12))
        self.entry_top_n.insert(0, "5")
        self.entry_top_n.grid(row=0, column=1, padx=5)

        # Button Frame
        btn_frame = tk.Frame(self.root, bg="#f5f5f5")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="📁 Load CSV", command=self.load_csv, bg="#4CAF50", fg="white", font=("Arial", 12), width=22).grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="📊 Show Sales Chart", command=self.show_sales_chart, bg="#2196F3", fg="white", font=("Arial", 12), width=22).grid(row=0, column=1, padx=10)
        tk.Button(btn_frame, text="⭐ Product Recommendations", command=self.show_recommendations, bg="#FF9800", fg="white", font=("Arial", 12), width=22).grid(row=0, column=2, padx=10)
        tk.Button(btn_frame, text="📈 Cluster Customers (AI)", command=self.cluster_customers, bg="#9C27B0", fg="white", font=("Arial", 12), width=22).grid(row=1, column=1, pady=10)
        tk.Button(btn_frame, text="🏆 Top Customers by Cluster", command=self.top_customers_by_cluster, bg="#3F51B5", fg="white", font=("Arial", 12), width=22).grid(row=1, column=2, pady=10)

        # Text Output
        self.output = tk.Text(self.root, height=18, width=110, font=("Consolas", 10))
        self.output.pack(pady=10)

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        try:
            self.df = pd.read_csv(file_path, encoding='ISO-8859-1')
            messagebox.showinfo("Success", "CSV File Loaded Successfully!")
            self.output.delete("1.0", tk.END)
            self.output.insert(tk.END, f"✅ Data Loaded. Total Rows: {len(self.df)}\n")
            self.output.insert(tk.END, f"Columns: {', '.join(self.df.columns)}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV: {str(e)}")

    def show_sales_chart(self):
        try:
            top_n = int(self.entry_top_n.get())
            top = self.df.groupby("Description")["Quantity"].sum().sort_values(ascending=False).head(top_n)
            fig, ax = plt.subplots(figsize=(9, 5))
            top.plot(kind='barh', ax=ax, color='#66bb6a')
            ax.set_title(f"Top {top_n} Best-Selling Products")
            ax.set_xlabel("Quantity Sold")
            ax.set_ylabel("Product Name")
            plt.tight_layout()

            chart_window = tk.Toplevel(self.root)
            chart_window.title("Top Selling Products Chart")
            canvas = FigureCanvasTkAgg(fig, master=chart_window)
            canvas.draw()
            canvas.get_tk_widget().pack()
        except Exception as e:
            messagebox.showerror("Error", f"Unable to generate chart: {str(e)}")

    def show_recommendations(self):
        try:
            self.output.delete("1.0", tk.END)
            top_n = int(self.entry_top_n.get())
            top_products = self.df.groupby("Description")["Quantity"].sum().sort_values(ascending=False).head(top_n)
            self.output.insert(tk.END, f"\n📦 Recommended Products for Future Sales (Top {top_n}):\n\n")
            for i, (product, qty) in enumerate(top_products.items(), 1):
                self.output.insert(tk.END, f"{i}. {product} (Sold: {int(qty)})\n")
        except Exception as e:
            messagebox.showerror("Error", f"Could not generate recommendations: {str(e)}")

    def cluster_customers(self):
        try:
            df = self.df.copy()
            df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]
            rfm = df.groupby("CustomerID").agg({
                "InvoiceDate": lambda x: (pd.Timestamp("now") - pd.to_datetime(x).max()).days,
                "InvoiceNo": "count",
                "TotalPrice": "sum"
            })
            rfm.columns = ["Recency", "Frequency", "Monetary"]
            kmeans = KMeans(n_clusters=3, random_state=42)
            rfm["Cluster"] = kmeans.fit_predict(rfm)
            self.rfm_clustered = rfm.reset_index()

            self.output.delete("1.0", tk.END)
            self.output.insert(tk.END, "📊 Customer Segmentation (KMeans Clustering):\n\n")
            self.output.insert(tk.END, rfm.groupby("Cluster").mean().round(1).to_string())
        except Exception as e:
            messagebox.showerror("Error", f"Clustering failed: {str(e)}")

    def top_customers_by_cluster(self):
        try:
            self.output.delete("1.0", tk.END)
            self.output.insert(tk.END, "\n🏆 Top Customers From Each Cluster:\n\n")
            for cluster_id in sorted(self.rfm_clustered['Cluster'].unique()):
                top_customers = self.rfm_clustered[self.rfm_clustered['Cluster'] == cluster_id].sort_values(by='Monetary', ascending=False).head(3)
                self.output.insert(tk.END, f"Cluster {cluster_id} Top Customers:\n")
                for idx, row in top_customers.iterrows():
                    self.output.insert(tk.END, f"  CustomerID: {int(row['CustomerID'])}, Recency: {int(row['Recency'])}, Frequency: {int(row['Frequency'])}, Monetary: {int(row['Monetary'])}\n")
                self.output.insert(tk.END, "\n")
        except Exception as e:
            messagebox.showerror("Error", f"Top customers extraction failed: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ECommerceDashboard(root)
    root.mainloop()
