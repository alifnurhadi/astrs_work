from matplotlib import pyplot as plt
from scipy import stats
import seaborn as sns
import numpy as np
import streamlit as st
import polars as pl
import plotly.express as px
import plotly.graph_objects as go



@st.cache_data
def load_data():
    master = pl.read_parquet('for_dashboard.parquet')
    return master
master = load_data()

# TOP ROW 
qa = master['Kota/Kabupaten','Provinsi','Status Pesanan','Returned quantity','Nomor Referensi SKU'].\
filter(pl.col('Returned quantity')== 0, pl.col('Status Pesanan')!= 'Batal')
# top provinsi popularity
qaa = qa['Provinsi'].value_counts(parallel=True, sort=True)[:15]['Provinsi'][0]
# revenue
tot_rev = master['Total Pembayaran'].sum()
# number sold
soldss = master.filter(pl.col('Provinsi')==qaa)['Jumlah'].sum()
# top prod 
top_prod = master.filter(pl.col('Provinsi')==qaa).group_by('Nomor Referensi SKU').agg(pl.col('total no dup').sum()).sort(by='total no dup',descending=True)[0].to_dicts()


# column kiri

ralies = master.filter(pl.col('month_days')<= '10-15')
slowsdown = master.filter(pl.col('month_days') > '10-15')
investigate1 = (ralies
 .group_by(['week_of_q4', 'Nomor Referensi SKU'])
 .agg([
     pl.len(),
     pl.col('total no dup').sum().alias('revenue')
 ])
 .sort(by=['week_of_q4', 'revenue'], descending=[False, True])
 .group_by('week_of_q4')
 .head(5)  # This will get top 5 SKUs by revenue for each week
)

investigate2 = (slowsdown
 .group_by(['week_of_q4', 'Nomor Referensi SKU'])
 .agg([
     pl.len(),
     pl.col('total no dup').sum().alias('revenue')
 ])
 .sort(by=['week_of_q4', 'revenue'], descending=[False, True])
 .group_by('week_of_q4')
 .head(5)  # This will get top 5 SKUs by revenue for each week
)

fig1 = px.bar(investigate1, x='week_of_q4', y='revenue', 
              color='Nomor Referensi SKU', title='Rallies Top 5 SKUs')
fig2 = px.bar(investigate2, x='week_of_q4', y='revenue', 
              color='Nomor Referensi SKU', title='Slowdown Top 5 SKUs')

# Combined figure can be created with:
combined_fig = go.Figure(data=fig1.data + fig2.data)

executive = master.group_by('Group_date').agg(pl.col('total no dup').sum()).sort('Group_date')
figpx = px.line( executive , x='Group_date' , y='total no dup')


with st.sidebar:
    filterbox = st.selectbox('choose :',['Executive','Correlation'])

def main():
    st.title('THIS IS OCTOBER DASHBOARD')
    cont_1 = st.container()
    cont_2 = st.container()
    with cont_1:
        st.success('this is inisde containers1')
        col11 , col12 ,col121, col13 = st.columns(4)
        col11.metric(label='Rank 1 Popularity',value=qaa ,help="this is revenue in month 6th")
        col12.metric(label='Total Revenue Generated ' ,value=f'{tot_rev:,.2f}' , help='October sales data')
        col121.metric(label='Jumlah Barang Terjual', value=f'{soldss:,.0f}', help='number of product sold based on popular provinsi')
        col13.metric(label='Top Product',value=f'{top_prod[0]["Nomor Referensi SKU"]}',help="this is tooltop")
        col13.write(f'value : {top_prod[0]["total no dup"]:,.0f} in sales')
        col14 , col15 , col16 , col17 = st.columns([1,2,2,1])
        col14.metric(label='Top Product',value='ini',help="this is tooltop")
        col15.metric(label='Top Product',value='lagi',help="this is tooltop")
        col16.metric(label='Top Product',value='uji',help="this is tooltop")
        col17.metric(label='Top Product',value='coba',help="this is tooltop")
        st.success('this is still inisde containers1')

    with cont_2:
        kiri ,kanan =st.columns(2)
        add , adf =kiri.columns(2)
        # kiri.success("This is in the container kiri")
        kiri.plotly_chart(combined_fig)
        with kiri.expander('insight from'):
            st.write('this is inside the expander will do')
        previous_value = 100
        current_value = 120
        percent_change = (current_value - previous_value) / previous_value * 100
        kiri.metric(label='Rank 1 Popularity', value=qaa, delta=f"{percent_change:.2f}%")
        kiri.success("This is in the container kiri")
        kanan.plotly_chart(figpx)
        kanan.success("This is in the container kanan")
        # add.plotly_chart(combined_fig)
        # adf.bar_chart(np.random.randn(50, 3))

# rev to disc relation
corr = master.group_by('Group_date').agg([pl.col('total no dup').sum().alias('total rev'),pl.col('ditanggung penjual no dup').sum().alias('total discount')]).sort(by='Group_date')
disc1 = corr.plot.scatter(y='total rev',x='total discount')

var1 = master['total no dup'].to_numpy()
var2 = master['ditanggung penjual no dup'].to_numpy()

corr , pval = stats.spearmanr(var1,var2)

def correlation():
    
    cont_1 = st.container()
    cont_2 = st.container()
    ataskiri , ataskanan = cont_1.columns(2)
    atkri1, atkri2 = ataskiri.columns(2)
    atkri1.altair_chart(disc1)
    with atkri1.expander(label='this is insight'):
        st.write(f'''correlation value"s are {corr} and pvalue is {pval:.5f} ,
                 it means whenever our store gave discount on the product the revenue tends to follow that eg. when our revenue is 1000000 around 37% (its squared of correlation value) of it can be achive because of discount strategies move by our company ''')
    atkri2.altair_chart(disc1)
    with atkri2.expander(label='this is insight'):
        st.write(f'''correlation value"s are {corr} and pvalue is {pval:.5f} ,
                 it means whenever our store gave discount on the product the revenue tends to follow that eg. when our revenue is 1000000 around 37% (its squared of correlatio''')
if __name__ == '__main__':
    main()