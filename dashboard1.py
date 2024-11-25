from matplotlib import pyplot as plt
import seaborn as sns
import numpy as np
import streamlit as st
import polars as pl
import plotly.express as px


st.set_page_config(layout='wide',initial_sidebar_state='collapsed')


@st.cache_data
def load_data():
    master = pl.read_parquet('final.parquet').with_columns(pl.col(['Pesanan Harus Dikirimkan Sebelum (Menghindari keterlambatan)','Waktu Pengiriman Diatur','Waktu Pesanan Dibuat',
        'Waktu Pembayaran Dilakukan','Waktu Pesanan Selesai']).str.to_datetime(format='%Y-%m-%d %H:%M' , strict=False)).sort(by=['Waktu Pengiriman Diatur'])
    return master


master = load_data()

qa = master['Kota/Kabupaten','Provinsi','Status Pesanan','Returned quantity','Nomor Referensi SKU'].\
filter(pl.col('Returned quantity')== 0, pl.col('Status Pesanan')!= 'Batal')
qaa = qa['Provinsi'].value_counts(parallel=True, sort=True)[:15]['Provinsi'][0]

tot_rev = master['Total Pembayaran'].sum()


def chart1 ():
    df1 = master['Waktu Pengiriman Diatur','Nomor Referensi SKU','Nama Variasi','Total Pembayaran','Harga Awal']
    df2 = master['Nomor Referensi SKU'].value_counts().sort(by='count',descending=True)[:20]
    sql = pl.SQLContext()
    sql.register_many({
    'd1':df1,
    'd2':df2
})
    query = '''
    select 
    d1."Waktu Pengiriman Diatur",
    d1."Harga Awal",
    d2."Nomor Referensi SKU",
    d1."Nama Variasi",
    d1."Total Pembayaran"
    From d2
    left join d1 on d2."Nomor Referensi SKU" == d1."Nomor Referensi SKU"

    '''
    answer = sql.execute(query=query).collect().sort(by='Waktu Pengiriman Diatur',descending=False).drop_nulls()
    fin1 = answer.with_columns(pl.col('Waktu Pengiriman Diatur').dt.date().alias('Agg Waktu')).group_by(['Agg Waktu','Nomor Referensi SKU']).agg(pl.col('Total Pembayaran').sum()).\
    sort(by='Agg Waktu')
    top10 = df2[:5]
    top20 = df2[5:15]
    top10lis = top10['Nomor Referensi SKU'].to_list()
    top20lis = top20['Nomor Referensi SKU'].to_list()
    line10 =fin1.filter(pl.col('Nomor Referensi SKU').is_in(top10lis)).with_columns(pl.col('Agg Waktu').dt.strftime('%Y-%m'))
    line20 =fin1.filter(pl.col('Nomor Referensi SKU').is_in(top20lis)).with_columns(pl.col('Agg Waktu').dt.strftime('%Y-%m'))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    # Plot the first lineplot on the first axis
    sns.lineplot(data=line10, x='Agg Waktu', y='Total Pembayaran', hue='Nomor Referensi SKU', ax=ax1 ,errorbar= None,markers='x')
    ax1.set_title('Product Movement the top 10 product by sales')
    ax1.set_xlabel('waktu')
    # ax1.set_xlim(['2024-07','2024-10'])

    # Plot the second lineplot on the second axis
    sns.lineplot(data=line20, x='Agg Waktu', y='Total Pembayaran', hue='Nomor Referensi SKU', ax=ax2 ,errorbar=None,markers="x")
    ax2.set_title('Potensial Product Movement the product by sales')
    ax2.set_xlabel('waktu')
    # ax2.set_xlim(['2024-07','2024-10'])

    # Adjust layout
    plt.tight_layout()

    # Show the plot
    return fig

def main():
    cont_1 = st.container()
    cont_2 = st.container()
    with cont_1:
        st.success('this is inisde containers1')
        col11 , col12 ,col121, col13 = st.columns(4)
        col11.metric(label='Rank 1 Popularity',value=qaa ,help="this is revenue in month 6th")
        col12.metric(label='Total Revenue Generated ' ,value=tot_rev , help='July - mid November data')
        col121.metric(label='Jumlah Barang Terjual', value='somevalue', help='July - mid November data')
        col13.metric(label='Top Product',value=np.random.choice(['saya' , 'kamu' , 'kami']),help="this is tooltop")
        col14 , col15 , col16 , col17 = st.columns([1,2,2,1])
        # col14.metric(label='Top Product',value=np.random.choice(['saya' , 'kamu' , 'kami']),help="this is tooltop")
        # col15.metric(label='Top Product',value=np.random.choice(['saya' , 'kamu' , 'kami']),help="this is tooltop")
        # col16.metric(label='Top Product',value=np.random.choice(['saya' , 'kamu' , 'kami']),help="this is tooltop")
        # col17.metric(label='Top Product',value=np.random.choice(['saya' , 'kamu' , 'kami']),help="this is tooltop")
        st.success('this is still inisde containers1')

    with cont_2:
        kiri ,kanan =st.columns(2)
        add , adf =kiri.columns(2)
        previous_value = 100
        current_value = 120
        percent_change = (current_value - previous_value) / previous_value * 100
        kiri.metric(label='Rank 1 Popularity', value=qaa, delta=f"{percent_change:.2f}%")
        kiri.success("This is in the container kri")
        kanan.pyplot(chart1())
        add.bar_chart(np.random.randn(50, 3))
        adf.bar_chart(np.random.randn(50, 3))



if __name__ == '__main__':
    main()