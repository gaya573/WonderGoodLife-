# 🚀 Deployment Guide

## 📦 Docker Compose로 배포 (EC2)

### 1. EC2 인스턴스 준비

```bash
# Docker & Docker Compose 설치
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. 프로젝트 배포

```bash
# 프로젝트 클론 or 복사
cd /home/ec2-user
git clone <repository-url>
cd batch-service-fastapi

# 환경 변수 설정
cp .env.example .env
vim .env

# Docker Compose 실행
cd deployment/docker
docker-compose up -d

# 로그 확인
docker-compose logs -f api
```

### 3. 포트 열기 (AWS Security Group)

| 서비스 | 포트 | 설명 |
|--------|------|------|
| FastAPI | 8000 | API 서버 |
| Flower | 5555 | Celery 모니터링 |
| MySQL | 3306 | 데이터베이스 (선택) |
| Redis | 6379 | 메시지 브로커 (선택) |

### 4. 접속

```
http://<EC2-PUBLIC-IP>:8000/docs
http://<EC2-PUBLIC-IP>:5555  (Flower)
```

## 🔄 업데이트

```bash
cd /home/ec2-user/batch-service-fastapi/deployment/docker

# 코드 업데이트
git pull

# 재시작
docker-compose down
docker-compose up -d --build
```

## 📊 모니터링

```bash
# 컨테이너 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f api
docker-compose logs -f celery_worker

# 리소스 사용량
docker stats
```

## 🛑 중지

```bash
# 서비스 중지
docker-compose down

# 볼륨까지 삭제 (데이터 초기화)
docker-compose down -v
```

## 💡 왜 Kubernetes 없이?

### ❌ Kubernetes가 필요한 경우
- 마이크로서비스 (10개+ 서비스)
- Auto Scaling 필요 (트래픽 변동 큼)
- 멀티 클라우드 배포

### ✅ Docker Compose가 충분한 경우 (현재)
- 모놀리식 아키텍처
- 관리자용 (트래픽 낮음)
- EC2 1대로 충분
- 단순한 배포 선호

**결론**: 현재는 Docker Compose가 최적! 🎯

## 🔧 트러블슈팅

### MySQL 연결 오류

```bash
# MySQL 상태 확인
docker-compose exec mysql mysqladmin ping -h localhost

# MySQL 로그 확인
docker-compose logs mysql
```

### Celery Worker 오류

```bash
# Worker 상태 확인 (Flower)
http://<EC2-IP>:5555

# Worker 로그 확인
docker-compose logs -f celery_worker
```

### 디스크 부족

```bash
# 사용하지 않는 이미지/컨테이너 정리
docker system prune -a
```

## 📝 환경 변수 (.env)

```env
# Database
DATABASE_URL=mysql+pymysql://wondergoodlife_user:wondergoodlife_pass123@mysql:3306/wondergoodlife_db

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# CORS
CORS_ORIGINS=["http://your-domain.com","http://localhost:5173"]
```

## 🎯 프로덕션 체크리스트

- [ ] 환경 변수 설정 (.env)
- [ ] Security Group 설정 (포트 8000, 5555)
- [ ] MySQL 비밀번호 변경
- [ ] 도메인 연결 (선택)
- [ ] HTTPS 설정 (Nginx + Let's Encrypt)
- [ ] 로그 모니터링 설정
- [ ] 백업 스크립트 설정

---

**EC2 + Docker Compose = 완벽! 🚀**

