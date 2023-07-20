from api.realis import Realis


if __name__ == "__main__":
    cur_year_sale_txns_df = Realis.extract_cur_year_sale_txns()
    cur_year_resale_txns_df = cur_year_sale_txns_df.pipe(
        lambda df: df[df["Type of Sale"] == "Resale"]
    )
    cur_year_resale_txns_df.to_csv("data/cur_year_resale_txns.csv")
