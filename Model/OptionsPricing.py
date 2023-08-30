import numpy as np
from scipy.stats import norm

# Config
TRADING_DAYS = 252
ACCURACY = 0.0001
IV_UP_BOUND = 2.


class BlackScholesModel:

    def d1(self, s: float, k: float, t: float, r: float, sigma: float):
        """Calculate d1 in Black-Scholes-Merton model

        Args:
            s (float): current underlying price
            k (float): strike price
            t (float): time to maturity (years)
            r (float): risk-free rate or financing rate
            sigma (float): annualized volatility

        Returns:
            float: d1
        """

        return (np.log(s/k) + (r + sigma ** 2 / 2) * t)/(sigma * np.sqrt(t))

    def d2(self, s: float, k: float, t: float, r: float, sigma: float):
        """Calculate d2 in Black-Scholes-Merton model

        Args:
            s (float): current underlying price
            k (float): strike price
            t (float): time to maturity (years)
            r (float): risk-free rate or financing rate
            sigma (float): annualized volatility

        Returns:
            float: d2
        """

        return self.d1(s, k, t, r, sigma) - sigma * np.sqrt(t)
    
    def premium(self, s: float, k: float, t: float, r: float, sigma: float, option_type: str):
        """Calculate theoretical option price in Black-Scholes-Merton model

        Args:
            s (float): current underlying price
            k (float): strike price
            t (float): time to maturity (years)
            r (float): risk-free rate or financing rate
            sigma (float): annualized volatility
            option_type (str): call or put

        Returns:
            float: theoretical option price (premium)
        """

        if t == 0:
            if option_type in ['Call', 'call', 'C', 'c']:
                return max(s - k, 0)
            elif option_type in ['Put', 'put', 'P', 'p']:
                return max(k - s, 0)
            else:
                raise ValueError('Option type must be either Call or Put')
        else:
            if option_type in ['Call', 'call', 'C', 'c']:
                return s * norm.cdf(self.d1(s, k, t, r, sigma)) - k * np.exp(-r * t) * norm.cdf(self.d2(s, k, t, r, sigma))
            elif option_type in ['Put', 'put', 'P', 'p']:
                return k * np.exp(-r * t) * norm.cdf(-self.d2(s, k, t, r, sigma)) - s * norm.cdf(-self.d1(s, k, t, r, sigma))
            else:
                raise ValueError('Option type must be either Call or Put')
    
    def delta(self, s: float, k: float, t: float, r: float, sigma: float, option_type: str):
        """Calculate delta in Black-Scholes-Merton model
        Instinct: If underlying price increases by one unit, how much does option price increase?

        Args:
            s (float): current underlying price
            k (float): strike price
            t (float): time to maturity (years)
            r (float): risk-free rate or financing rate
            sigma (float): annualized volatility
            option_type (str): call or put

        Returns:
            float: delta
        """
        if option_type in ['Call', 'call', 'C', 'c']:
            return norm.cdf(self.d1(s, k, t, r, sigma))
        elif option_type in ['Put', 'put', 'P', 'p']:
            return norm.cdf(self.d1(s, k, t, r, sigma)) - 1
        else:
            raise ValueError('Option type must be either Call or Put')
    
    def gamma_one_percent(self, s: float, k: float, t: float, r: float, sigma: float, option_type: str):
        """Calculate gamma one percent in Black-Scholes-Merton model, using difference method
        Instinct: The impact of one percent underlying price change on option's delta

        Args:
            s (float): current underlying price
            k (float): strike price
            t (float): time to maturity (years)
            r (float): risk-free rate or financing rate
            sigma (float): annualized volatility
            option_type (str): call or put

        Returns:
            float: 1% gamma
        """

        return self.delta(s * 1.005, k, t, r, sigma, option_type) - self.delta(s * 0.995, k, t, r, sigma, option_type)
    
    def vega_one_percent(self, s: float, k: float, t: float, r: float, sigma: float, option_type: str):
        """Calculate vega one percent difference in Black-Scholes-Merton model, using difference method
        Instinct: The impact of one percent change in volatility on option price
        
        Args:
            s (float): current underlying price
            k (float): strike price
            t (float): time to maturity (years)
            r (float): risk-free rate or financing rate
            sigma (float): annualized volatility
            option_type (str): call or put

        Returns:
            float: 1% vega        
        """

        return self.premium(s, k, t, r, sigma + 0.005, option_type) - self.premium(s, k, t, r, sigma - 0.005, option_type)
    
    def theta_one_day(self, s: float, k: float, t: float, r: float, sigma: float, option_type: str):
        """Calculate theta one day in Black-Scholes-Merton model, using difference method
        Instinct: The impact of one day pass in time to maturity on option price
        
        Args:
            s (float): current underlying price
            k (float): strike price
            t (float): time to maturity (years)
            r (float): risk-free rate or financing rate
            sigma (float): annualized volatility
            option_type (str): call or put
        
        Returns:
            float: 1 day theta
        """
        
        return self.premium(s, k, t - 1 / TRADING_DAYS, r, sigma, option_type) - self.premium(s, k, t, r, sigma, option_type)
    
    def rho_one_percent(self, s: float, k: float, t: float, r: float, sigma: float, option_type: str):
        """Calculate rho one percent in Black-Scholes-Merton model, using difference method
        Instinct: The impact of one percent change in interest rate on option price
        
        Args:
            s (float): current underlying price
            k (float): strike price
            t (float): time to maturity (years)
            r (float): risk-free rate or financing rate
            sigma (float): annualized volatility
            option_type (str): call or put        

        Returns:
            float: 1% rho
        """
        return self.premium(s, k, t, r + 0.005, sigma, option_type) - self.premium(s, k, t, r - 0.005, sigma, option_type)


def calc_implied_volatility(s: float, k: float, t: float, r: float, premium: float, option_type: str):
    Calculator = BlackScholesModel()
    accuracy = ACCURACY
    Low_bound = ACCURACY
    Up_bound = IV_UP_BOUND

    if (Calculator.premium(s,k,t,r,Low_bound,option_type) - premium) * (Calculator.premium(s,k,t,r,Up_bound,option_type) - premium) <0:
        
        while (Up_bound - Low_bound)/2 >= accuracy:
            Mid = (Up_bound + Low_bound)/2.
            
            if (Calculator.premium(s,k,t,r,Mid,option_type) - premium) * (Calculator.premium(s,k,t,r,Low_bound,option_type) - premium) <0:
                Up_bound = Mid
            elif (Calculator.premium(s,k,t,r,Mid,option_type) - premium) * (Calculator.premium(s,k,t,r,Up_bound,option_type) - premium) <0:
                Low_bound = Mid
            
            else:
                Up_bound = Mid
                Low_bound = Mid
                
        ImpVol = (Up_bound + Low_bound)/2
        return ImpVol
    else:
        raise Exception('Error! Implied Volatility is not in the range of 0 to 2. Please check premium input.')


if __name__ == '__main__':
    calc = BlackScholesModel()
    print(calc.premium(100, 105, 60/252, 0.02, 0.3, 'call'))
    print(calc.delta(100, 100, 1, 0.05, 0.2, 'call'))
    print(calc.gamma_one_percent(100, 100, 1, 0.05, 0.2, 'call'))
    print(calc.vega_one_percent(100, 100, 1, 0.05, 0.2, 'call'))
    print(calc.theta_one_day(100, 100, 1, 0.05, 0.2, 'call'))
    print(calc.rho_one_percent(100, 100, 1, 0.05, 0.2, 'call'))