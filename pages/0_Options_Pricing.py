import streamlit as st
import pandas as pd
import sys

from Model import OptionsPricing

st.set_page_config(page_title='Options Pricing', page_icon=':chart_with_upwards_trend:', layout='wide', initial_sidebar_state='auto')
st.title('Options Pricing')

with st.sidebar:
    st.write('### Input Parameters')
    option_type = st.selectbox('Option Type',('Call', 'Put'))
    s = st.number_input('Spot', value=100.0, min_value=0.01, max_value = 1000000.)
    k = st.number_input('Strike', value=110.0, min_value=0.01, max_value = 1000000.)
    if option_type == 'Call':
        if k > s:
            st.write(f"OTM: {round((k-s)/s*100,2)}%")
        elif k == s:
            st.write("ATM: 0%")
        else:
            st.write(f"ITM: {round((s-k)/s*100,2)}%")
    else:
        if k > s:
            st.write(f"ITM: {round((k-s)/s*100,2)}%")
        elif k == s:
            st.write("ATM: 0%")
        else:
            st.write(f"OTM: {round((s-k)/s*100,2)}%")

    t = st.slider('Remain Trading Days', min_value = 0, max_value = 252, value = 22)
    r = st.slider('Interest Rate(%)', min_value = 0.01, max_value = 10., value = 2., step=0.01, help='Risk-free rate or financing rate')
    sigma = st.slider('Volatility(%)', min_value = 0.01, max_value = 200., value = 30., step=1.)
    st.divider()
    st.write("### Position Settings")
    multiplier = st.number_input('Multiplier', value=1000, min_value=1, max_value = 1000000)
    position = st.selectbox('Position',('Long', 'Short'))
    qty = st.number_input('Quantity', value=10, min_value=1, max_value = 1000000)


Calculator = OptionsPricing.BlackScholesModel()
st.metric(label="Premium", value=round(Calculator.premium(s, k, t/252, r/100, sigma/100, option_type), 4))

premium = round(Calculator.premium(s, k, t/252, r/100, sigma/100, option_type), 4)
delta = round(Calculator.delta(s, k, t/252, r/100, sigma/100, option_type), 4)
gamma = round(Calculator.gamma_one_percent(s, k, t/252, r/100, sigma/100, option_type), 4)
theta = round(Calculator.theta_one_day(s, k, t/252, r/100, sigma/100, option_type), 4)
vega = round(Calculator.vega_one_percent(s, k, t/252, r/100, sigma/100, option_type), 4)
rho = round(Calculator.rho_one_percent(s, k, t/252, r/100, sigma/100, option_type), 4)
if position == 'Long':
    qty = qty
else:
    qty = -qty

def style_negative(v, props=''):
    return props if v < 0 else None

pricing_results = pd.DataFrame(columns = ['Premium','Delta','Gamma(1%)','Theta(1d)','Vega(1%)','Rho(1%)'], index = ['Unit','Position ($)'])
pricing_results['Premium'] = [premium, premium * multiplier * qty]
pricing_results['Delta'] = [delta, delta * s * multiplier * qty]
pricing_results['Gamma(1%)'] = [gamma, gamma * s * multiplier * qty]
pricing_results['Theta(1d)'] = [theta, theta * multiplier * qty]
pricing_results['Vega(1%)'] = [vega, vega * multiplier * qty]
pricing_results['Rho(1%)'] = [rho, rho * multiplier * qty]

st.dataframe(pricing_results, use_container_width=True)

st.divider()

st.write('### Delta Neutral')

hedge_qty = '{:,.0f}'.format(abs(round(-delta * multiplier * qty,0)))

if -delta * multiplier * qty > 0:
    st.info(f'##### Buy {hedge_qty} shares of underlying asset')
else:
    st.info(f'##### Sell {hedge_qty} shares of underlying asset')

