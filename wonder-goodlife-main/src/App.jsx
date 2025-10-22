import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/layout/Header';
import Footer from './components/layout/Footer';
import QuickConsult from './components/layout/QuickConsult';
import Home from './pages/Home/Home';
import CarList from './pages/Car/CarList';
import CarDetail from './pages/Car/CarDetail';
import ExpressDealDetail from './pages/ExpressDeals/ExpressDealDetail';
import PrepurchaseDealDetail from './pages/PrepurchaseDeals/PrepurchaseDealDetail';
import ExpressDeals from './pages/ExpressDeals/ExpressDeals';
import ExpressDealsAll from './pages/ExpressDeals/ExpressDealsAll';
import PrepurchaseDeals from './pages/PrepurchaseDeals/PrepurchaseDeals';
import Promotion from './pages/CarPromotion/Promotion';
import CardPromotion from './pages/CardPromoiton/CardPromotion';
import CardPromotionBrands from './pages/CardPromoiton/CardPromotionBrands';
import CardPromotionDetail from './pages/CardPromoiton/CardPromotionDetail';
import PromotionBrands from './pages/CarPromotion/PromotionBrands';
import PromotionDetail from './pages/CarPromotion/PromotionDetail';
import Review from './pages/Review/Review';
import ReviewWrite from './pages/Review/ReviewWrite';
// 전역 스타일 최소화: 리셋/변수만 유지. 페이지/컴포넌트 스타일은 모두 CSS Modules로 격리
import './App.css';

function App() {
  return (
    <div className="app">
      <Header />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/carlist" element={<Navigate to="/carlist/domestic" replace />} />
        <Route path="/carlist/:carType" element={<CarList />} />
        <Route path="/car-detail/:carId" element={<CarDetail />} />
        <Route path="/express-deals" element={<ExpressDeals />} />
        <Route path="/express-deals/detail/:carId" element={<ExpressDealDetail />} />
        <Route path="/express-deals/all" element={<ExpressDealsAll />} />
        <Route path="/prepurchase-deals" element={<PrepurchaseDeals />} />
        <Route path="/prepurchase-deals/detail/:carId" element={<PrepurchaseDealDetail />} />
        <Route path="/promotion" element={<Promotion />} />
        <Route path="/card-promotion" element={<CardPromotion />} />
        <Route path="/card-promotion/brands" element={<CardPromotionBrands />} />
        <Route path="/card-promotion/brands/detail/:id" element={<CardPromotionDetail />} />
        <Route path="/promotion/brands" element={<PromotionBrands />} />
        <Route path="/promotion/brands/detail/:id" element={<PromotionDetail />} />
        <Route path="/review" element={<Review />} />
        <Route path="/review/write" element={<ReviewWrite />} />
      </Routes>
      <Footer />
      <QuickConsult />
    </div>
  );
}

export default App; 