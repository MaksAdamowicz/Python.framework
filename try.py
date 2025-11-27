import pandas as pd
import matplotlib.pyplot as plt
import smtplib
import ssl
from email.message import EmailMessage
import os

def test_if_works():
    print("The stock price exceeded the treshold!")

def send_email_to_example(subject, body, sender_email, sender_password):
    
    receiver_email = "example@gmail.com"

    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    smtp_server = "smtp.gmail.com"
    port = 465  

    context = ssl.create_default_context()

    try:
        print(f"Connecting to {smtp_server}...")
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print(f"✅ Email successfully sent to {receiver_email}!")
            
    except smtplib.SMTPAuthenticationError:
        print("❌ Authentication Error: Please check your email and App Password.")
    except Exception as e:
        print(f"❌ An error occurred: {e}")

def process_stock_data(csv_path):
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return None, None

    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()

    if 'Low' in df.columns:
        df['Low'] = df['Low'].astype(str).str.replace('$', '').astype(float)
    if 'Open' in df.columns:
        df['Open'] = df['Open'].astype(str).str.replace('$', '').astype(float)

    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')

    
    df_2017 = df[df['Date'].dt.year == 2017].copy()
    monthly_avg_2017 = df_2017.groupby(df_2017['Date'].dt.month)['Low'].mean()

    print("2017 Monthly Averages:")
    print(monthly_avg_2017)


    df_2018 = df[df['Date'].dt.year == 2018].copy()
    df_2018['Month'] = df_2018['Date'].dt.month
    df_2018['Avg_2017'] = df_2018['Month'].map(monthly_avg_2017)

    df_2018['Lower_Bound'] = df_2018['Avg_2017'] * 0.40
    df_2018['Upper_Bound'] = df_2018['Avg_2017'] * 1.10

    df_2018['In_Range'] = (df_2018['Low'] >= df_2018['Lower_Bound']) & \
                          (df_2018['Low'] <= df_2018['Upper_Bound'])

    return df_2018, monthly_avg_2017

if __name__ == "__main__":
  
    MY_EMAIL = "your_actual_email@gmail.com"
    MY_APP_PASSWORD = "your_16_char_app_password"
    CSV_FILE = 'HistoricalQuotes.csv'

  
    df_2018, monthly_avgs = process_stock_data(CSV_FILE)

    if df_2018 is not None:
        outliers = df_2018[~df_2018['In_Range']]


        # if not outliers.empty:
        #     print(f"\nFound {len(outliers)} outliers. Sending individual emails...")

        #     for index, row in outliers.iterrows():
                
              
        #         subject = f"Alert: Outlier detected on {row['Date'].date()}"
        #         body = (
        #             f"Date: {row['Date'].date()}\n"
        #             f"Price: {row['Low']}\n"
        #             f"Limit Range: {row['Lower_Bound']:.2f} to {row['Upper_Bound']:.2f}\n"
        #         )
        #         if MY_EMAIL != "your_actual_email@gmail.com":
        #             send_email_to_example(subject, body, MY_EMAIL, MY_APP_PASSWORD)
        #         else:
        #             print(f"Would send email for {row['Date'].date()}")


        if not outliers.empty:
          print(f"\nFound {len(outliers)} outliers.")
          print("TEST MODE: Calling test_if_works() instead of sending email...\n")

          for index, row in outliers.iterrows():
              test_if_works()

              print(f"Test triggered for: {row['Date'].date()} - Price {row['Low']}")

        else:
            print("No outliers found.")

    
        plt.figure(figsize=(12, 6))
        plt.plot(df_2018['Date'], df_2018['Low'], label='2018 Daily Low', color='blue')
        plt.plot(df_2018['Date'], df_2018['Upper_Bound'], color='red', linestyle='--', label='110% Limit')
        plt.plot(df_2018['Date'], df_2018['Lower_Bound'], color='green', linestyle='--', label='40% Limit')
        
        plt.fill_between(df_2018['Date'], 
                        df_2018['Lower_Bound'], 
                        df_2018['Upper_Bound'], 
                        color='gray', alpha=0.2)

        if not outliers.empty:
            plt.scatter(outliers['Date'], outliers['Low'], color='orange', zorder=5, label='Outliers')

        plt.title('2018 Performance Analysis')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()