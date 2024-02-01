Simple scraper for Steam price check for each CS2 case, using Python with Beautifulsoup4 & PostgreSQL as db.

If you want to use the Scraper, please install Postgre and use this query to build it up and run the code.:

```
CREATE TABLE case_prices (
    id SERIAL PRIMARY KEY,
    case_name VARCHAR(255),
    case_price VARCHAR(50),
    latest_date_checked TIMESTAMP
);
```

Additionally, the execute file prints the table in cmd as shown in below picture.
![alt text](https://i.imgur.com/G45KL4Z.png)
