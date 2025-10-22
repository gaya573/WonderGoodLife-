import { useState, useEffect, useMemo, useCallback } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import versionAPI from '../../services/versionApi';

/**
 * 검색 기능 커스텀 훅 - 데이터베이스 직접 검색
 * 브랜드, 모델, 트림, 옵션에 대한 실시간 검색 및 미리보기 기능 제공
 */
export const useSearch = (selectedVersion) => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [searchStats, setSearchStats] = useState({
    totalBrands: 0,
    totalModels: 0,
    totalTrims: 0,
    totalOptions: 0,
    totalItems: 0
  });

  // 검색어 상태 - URL 파라미터와 동기화
  const [searchQuery, setSearchQuery] = useState('');
  
  // URL에서 검색 파라미터 읽기
  const urlSearchParam = searchParams.get('search') || '';

  // 데이터베이스 검색 실행
  const searchDatabase = useCallback(async (query, searchType = 'all', limit = 20) => {
    if (!selectedVersion?.id || !query.trim()) {
      return { results: [], stats: { totalItems: 0 } };
    }

    try {
      console.log('🔍 검색 시작:', { query, searchType, versionId: selectedVersion.id });
      const response = await versionAPI.searchData(selectedVersion.id, query, searchType, 20);
      const data = response.data;
      console.log('🔍 검색 결과:', data);
      
      // 백엔드 응답 구조에 맞게 검색 결과 처리
      const allResults = [];
      let brandCount = 0;
      let modelCount = 0;
      let trimCount = 0;
      let optionCount = 0;
      
      // 강화된 중복 제거를 위한 Set
      const addedItems = new Set(); // 모든 항목의 고유 키 저장

      // 검색 결과를 타입별로 분류하여 처리 (브랜드, 모델, 트림 전체 검색)
      data.results.forEach(item => {
        switch (item.type) {
          case 'brand':
            const brandKey = `brand_${item.id}_${item.name}`;
            if (!addedItems.has(brandKey)) {
              allResults.push({
                id: item.id,
                name: item.name,
                type: 'brand',
                displayText: `brand:${item.name}`,
                subtitle: '브랜드',
                originalData: item,
                score: item.match_score || 100
              });
              addedItems.add(brandKey);
              brandCount++;
            }
            break;
            
          case 'model':
            const modelKey = `model_${item.id}_${item.name}`;
            if (!addedItems.has(modelKey)) {
              allResults.push({
                id: item.id,
                name: item.name,
                type: 'model',
                displayText: `brand:${item.brand_name} model:${item.name}`,
                subtitle: `${item.brand_name} 모델`,
                originalData: item,
                score: item.match_score || 80
              });
              addedItems.add(modelKey);
              modelCount++;
            }
            break;
            
          case 'trim':
            const trimKey = `trim_${item.id}_${item.name}_${item.brand_name}_${item.model_name}`;
            if (!addedItems.has(trimKey)) {
              allResults.push({
                id: item.id,
                name: item.name,
                type: 'trim',
                displayText: `brand:${item.brand_name} model:${item.model_name} trim:${item.name}`,
                subtitle: `${item.brand_name} ${item.model_name} 트림`,
                originalData: item,
                score: item.match_score || 70
              });
              addedItems.add(trimKey);
              trimCount++;
            }
            break;
        }
      });
      
      // 백엔드에서 이미 정렬된 결과를 그대로 사용 (점수 높은 순)
      return {
        results: allResults.slice(0, 20), // 상위 20개만 표시 (중복 방지)
        stats: {
          totalBrands: brandCount,
          totalModels: modelCount,
          totalTrims: trimCount,
          totalOptions: optionCount,
          totalItems: data.total_count
        }
      };
    } catch (error) {
      console.error('데이터베이스 검색 실패:', error);
      
      // 네트워크 에러인 경우 재시도 로직
      if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
        console.log('🔄 네트워크 에러 감지, 재시도 중...');
        try {
          // 1초 후 재시도
          await new Promise(resolve => setTimeout(resolve, 1000));
          const retryResponse = await versionAPI.searchData(selectedVersion.id, query, searchType, 20);
          const retryData = retryResponse.data;
          
          const allResults = [];
          let brandCount = 0;
          let modelCount = 0;
          let trimCount = 0;
          let optionCount = 0;
          
          retryData.results.forEach(item => {
            switch (item.type) {
              case 'brand':
                allResults.push({
                  id: item.id,
                  name: item.name,
                  type: 'brand',
                  displayText: `brand:${item.name}`,
                  subtitle: '브랜드',
                  originalData: item,
                  score: item.match_score || 100
                });
                brandCount++;
                break;
              case 'model':
                allResults.push({
                  id: item.id,
                  name: item.name,
                  type: 'model',
                  displayText: `brand:${item.brand_name} model:${item.name}`,
                  subtitle: `${item.brand_name} 모델`,
                  originalData: item,
                  score: item.match_score || 80
                });
                modelCount++;
                break;
              case 'trim':
                allResults.push({
                  id: item.id,
                  name: item.name,
                  type: 'trim',
                  displayText: `brand:${item.brand_name} model:${item.model_name} trim:${item.name}`,
                  subtitle: `${item.brand_name} ${item.model_name} 트림`,
                  originalData: item,
                  score: item.match_score || 70
                });
                trimCount++;
                break;
            }
          });
          
          return {
            results: allResults.slice(0, 20),
            stats: {
              totalBrands: brandCount,
              totalModels: modelCount,
              totalTrims: trimCount,
              totalOptions: optionCount,
              totalItems: retryData.total_count
            }
          };
        } catch (retryError) {
          console.error('재시도도 실패:', retryError);
        }
      }
      
      return { results: [], stats: { totalItems: 0 } };
    }
  }, [selectedVersion?.id]);

  // 퍼지 검색 알고리즘
  const fuzzySearch = useCallback((query, text) => {
    if (!query || !text) return { score: 0, matches: [] };
    
    const queryLower = query.toLowerCase();
    const textLower = text.toLowerCase();
    
    // 정확한 매치
    if (textLower.includes(queryLower)) {
      return { score: 100, matches: [{ start: textLower.indexOf(queryLower), end: textLower.indexOf(queryLower) + queryLower.length }] };
    }
    
    // 부분 매치 (연속된 문자들)
    let score = 0;
    let queryIndex = 0;
    const matches = [];
    let currentMatch = null;
    
    for (let i = 0; i < textLower.length && queryIndex < queryLower.length; i++) {
      if (textLower[i] === queryLower[queryIndex]) {
        if (!currentMatch) {
          currentMatch = { start: i, end: i };
        } else {
          currentMatch.end = i;
        }
        score += queryIndex === 0 ? 10 : 5; // 첫 번째 문자에 더 높은 점수
        queryIndex++;
      } else if (currentMatch && queryIndex > 0) {
        matches.push(currentMatch);
        currentMatch = null;
      }
    }
    
    if (currentMatch) {
      matches.push(currentMatch);
    }
    
    // 모든 쿼리 문자가 매치되었는지 확인
    if (queryIndex === queryLower.length) {
      score += 20; // 완전 매치 보너스
    }
    
    return { score, matches };
  }, []);

  // 검색 실행 (디바운싱 적용) - URL 파라미터가 아닌 경우에만 실행
  useEffect(() => {
    // URL 파라미터에서 온 검색어가 아닌 경우에만 실행
    if (searchQuery && searchQuery !== urlSearchParam) {
      if (!searchQuery.trim()) {
        setSearchResults([]);
        setShowPreview(false);
        setSearchStats({ totalBrands: 0, totalModels: 0, totalTrims: 0, totalOptions: 0, totalItems: 0 });
        return;
      }

      setIsSearching(true);
      const timeoutId = setTimeout(async () => {
        try {
          const { results, stats } = await searchDatabase(searchQuery);
          setSearchResults(results);
          setSearchStats(stats);
          setShowPreview(true);
        } catch (error) {
          console.error('검색 중 오류 발생:', error);
          setSearchResults([]);
          setSearchStats({ totalBrands: 0, totalModels: 0, totalTrims: 0, totalOptions: 0, totalItems: 0 });
        } finally {
          setIsSearching(false);
        }
      }, 500); // 500ms 디바운싱

      return () => clearTimeout(timeoutId);
    }
  }, [searchQuery, searchDatabase, urlSearchParam]); // urlSearchParam 의존성 추가

  // 검색어 하이라이트 함수
  const highlightText = useCallback((text, matches) => {
    if (!matches || matches.length === 0) return text;
    
    let highlightedText = text;
    let offset = 0;
    
    // 매치된 부분을 하이라이트
    matches.forEach(match => {
      const before = highlightedText.slice(0, match.start + offset);
      const matched = highlightedText.slice(match.start + offset, match.end + offset + 1);
      const after = highlightedText.slice(match.end + offset + 1);
      
      highlightedText = `${before}<mark style="background: #fef3c7; color: #92400e; padding: 0.125rem 0.25rem; border-radius: 0.25rem;">${matched}</mark>${after}`;
      offset += 52; // 하이라이트 태그 길이 보정
    });
    
    return highlightedText;
  }, []);

  // 검색어 설정 (내부 상태만 업데이트)
  const handleSearchChange = useCallback((value) => {
    setSearchQuery(value.trim());
  }, []);

  // 검색 결과 선택 - URL은 상위 컴포넌트에서 관리
  const selectSearchResult = useCallback((result) => {
    console.log('🔍 useSearch - selectSearchResult 호출됨:', result);
    
    // 검색 결과 초기화
    setSearchResults([]);
    setShowPreview(false);
    
    // URL 파라미터 업데이트 (React Router와 동기화)
    const newSearchParams = new URLSearchParams(searchParams);
    const searchValue = result.displayText || result.name;
    newSearchParams.set('search', searchValue);
    
    // React Router의 navigate 사용으로 상태 동기화
    setSearchParams(newSearchParams, { replace: true });
    
    console.log('🔍 useSearch - selectSearchResult 완료, result 반환:', result);
    return result;
  }, [searchParams, setSearchParams]);

  // 검색 초기화 - URL 파라미터도 제거
  const clearSearch = useCallback(() => {
    // 검색어 초기화
    setSearchQuery('');
    
    // URL에서 검색 파라미터 제거
    const newSearchParams = new URLSearchParams(searchParams);
    newSearchParams.delete('search');
    setSearchParams(newSearchParams, { replace: true });
    
    setSearchResults([]);
    setShowPreview(false);
  }, [searchParams, setSearchParams]);

  // 검색 제출 (버튼 클릭 또는 Enter) - 첫 번째 결과로 이동
  const submitSearch = useCallback(async (query) => {
    if (!selectedVersion?.id || !query.trim()) {
      return;
    }

    setIsSearching(true);
    try {
      const { results, stats } = await searchDatabase(query);
      
      // 첫 번째 결과가 있으면 해당 결과로 이동
      if (results && results.length > 0) {
        const firstResult = results[0];
        
        // 내부 상태 업데이트
        setSearchQuery(firstResult.displayText || firstResult.name);
        setSearchResults([]);
        setShowPreview(false);
        
        // URL 파라미터 업데이트 (React Router와 동기화)
        const newSearchParams = new URLSearchParams(searchParams);
        const searchValue = firstResult.displayText || firstResult.name;
        newSearchParams.set('search', searchValue);
        
        // React Router의 navigate 사용으로 상태 동기화
        setSearchParams(newSearchParams, { replace: true });
        
        return { results: [firstResult], stats };
      } else {
        // 결과가 없으면 미리보기만 표시
        setSearchResults([]);
        setSearchStats(stats);
        setShowPreview(true);
        return { results: [], stats };
      }
    } catch (error) {
      console.error('검색 제출 중 오류 발생:', error);
      setSearchResults([]);
      setSearchStats({ totalBrands: 0, totalModels: 0, totalTrims: 0, totalOptions: 0, totalItems: 0 });
      throw error;
    } finally {
      setIsSearching(false);
    }
  }, [selectedVersion?.id, searchDatabase, searchParams, setSearchParams]);

  // 검색 통계는 상태로 관리 (데이터베이스에서 가져옴)

  // URL 파라미터 기반 검색 실행 (무한 루프 방지)
  useEffect(() => {
    // URL 파라미터가 변경된 경우에만 실행
    if (urlSearchParam && selectedVersion?.id) {
      console.log('🔍 URL 파라미터에서 검색어 감지:', urlSearchParam);
      
      // 내부 검색어 상태 업데이트
      setSearchQuery(urlSearchParam);
      
      // URL 검색어로 검색 실행
      const executeUrlSearch = async () => {
        try {
          console.log('🔍 URL 검색 실행 시작...');
          const result = await searchDatabase(urlSearchParam, 'all');
          console.log('🔍 URL 검색 결과:', result);
          setSearchResults(result.results);
          setSearchStats(result.stats);
          setShowPreview(true);
        } catch (error) {
          console.error('🔍 URL 검색 실행 실패:', error);
          setSearchResults([]);
          setSearchStats({ totalBrands: 0, totalModels: 0, totalTrims: 0, totalOptions: 0, totalItems: 0 });
          setShowPreview(false);
        }
      };
      
      executeUrlSearch();
    } else if (!urlSearchParam) {
      // URL에 검색 파라미터가 없으면 검색 결과 초기화
      console.log('🔍 검색 파라미터 없음, 초기화');
      setSearchQuery('');
      setSearchResults([]);
      setSearchStats({ totalBrands: 0, totalModels: 0, totalTrims: 0, totalOptions: 0, totalItems: 0 });
      setShowPreview(false);
    }
  }, [urlSearchParam, selectedVersion?.id]); // searchQuery 의존성 제거로 무한 루프 방지

  return {
    // 상태
    searchQuery, // 내부 상태로 관리되는 검색어
    searchResults,
    isSearching,
    showPreview,
    searchStats,
    
    // 액션
    handleSearchChange,
    selectSearchResult,
    clearSearch,
    submitSearch,
    highlightText,
    
    // 유틸리티
    hasResults: searchResults.length > 0
  };
};
