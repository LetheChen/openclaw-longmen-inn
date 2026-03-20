# 测试规范文档 (Testing Guidelines)

> 📋 本规范定义了龙门客栈业务管理系统的测试策略和具体规范  
> 📅 版本：v1.0  
> 👤 维护者：账房先生（质量保证工程师）

---

## 目录

1. [测试策略和分层](#测试策略和分层)
2. [单元测试规范](#单元测试规范)
3. [API测试规范](#api测试规范)
4. [前端组件测试规范](#前端组件测试规范)
5. [测试覆盖率要求](#测试覆盖率要求)

---

## 测试策略和分层

### 测试金字塔

```
         /\
        /  \
       / E2E \      <- 端到端测试 (少量)
      /--------\
     /          \
    / Integration \   <- 集成测试 (中等)
   /----------------\
  /                  \
 /    Unit Tests       \  <- 单元测试 (大量)
/________________________\
```

### 测试分层策略

| 层级 | 测试类型 | 比例 | 执行时间 | 工具 |
|------|----------|------|----------|------|
| L1 | 单元测试 | 70% | < 5分钟 | pytest, Jest |
| L2 | 集成测试 | 20% | < 15分钟 | pytest-asyncio, MSW |
| L3 | E2E测试 | 10% | < 30分钟 | Playwright |

### 测试原则

1. **自动化优先**：所有测试都应该可以自动执行
2. **快速反馈**：单元测试应该在几秒钟内完成
3. **独立执行**：每个测试应该可以独立运行，不依赖其他测试
4. **可重复**：测试结果应该稳定，不依赖外部状态
5. **可读性**：测试代码应该清晰易读，是活的文档

---

## 单元测试规范

### 1. Python后端单元测试

**测试框架**：pytest + pytest-asyncio + pytest-cov

**目录结构**：

```
backend/
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   └── services/
└── tests/              # 测试目录
    ├── __init__.py
    ├── conftest.py     # 测试配置和fixture
    ├── unit/           # 单元测试
    │   ├── __init__.py
    │   ├── test_services/
    │   ├── test_models/
    │   └── test_utils/
    └── integration/    # 集成测试
        ├── __init__.py
        └── test_api/
```

**测试命名规范**：

```python
# 测试文件命名：test_*.py
# 测试类命名：Test* (可选)
# 测试函数命名：test_*

# ✅ 良好示例
# tests/unit/test_services/test_booking_service.py

import pytest
from datetime import date, timedelta
from app.services.booking_service import BookingService
from app.models.booking import BookingStatus

class TestBookingService:
    """预订服务测试。"""
    
    @pytest.fixture
    def service(self):
        """创建服务实例。"""
        return BookingService()
    
    @pytest.fixture
    def sample_booking_data(self):
        """示例预订数据。"""
        return {
            'customer_name': '张三',
            'phone': '13800138000',
            'room_id': 'room-001',
            'check_in': date.today() + timedelta(days=1),
            'check_out': date.today() + timedelta(days=3),
        }
    
    async def test_create_booking_success(self, service, sample_booking_data):
        """测试成功创建预订。"""
        # Act
        booking = await service.create_booking(**sample_booking_data)
        
        # Assert
        assert booking is not None
        assert booking.customer_name == sample_booking_data['customer_name']
        assert booking.status == BookingStatus.PENDING
    
    async def test_create_booking_invalid_phone(self, service, sample_booking_data):
        """测试无效手机号应抛出异常。"""
        # Arrange
        sample_booking_data['phone'] = 'invalid-phone'
        
        # Act & Assert
        with pytest.raises(ValueError, match='手机号格式不正确'):
            await service.create_booking(**sample_booking_data)
    
    async def test_create_booking_past_check_in(self, service, sample_booking_data):
        """测试过去日期应抛出异常。"""
        # Arrange
        sample_booking_data['check_in'] = date.today() - timedelta(days=1)
        
        # Act & Assert
        with pytest.raises(ValueError, match='入住日期不能是过去日期'):
            await service.create_booking(**sample_booking_data)
    
    async def test_calculate_total_nights(self, service):
        """测试住宿天数计算。"""
        # Arrange
        check_in = date(2024, 3, 1)
        check_out = date(2024, 3, 5)
        
        # Act
        nights = service.calculate_nights(check_in, check_out)
        
        # Assert
        assert nights == 4
    
    async def test_cancel_confirmed_booking(self, service, sample_booking_data):
        """测试取消已确认预订。"""
        # Arrange
        booking = await service.create_booking(**sample_booking_data)
        booking = await service.confirm_booking(booking.id)
        
        # Act
        cancelled = await service.cancel_booking(booking.id, reason='客户要求')
        
        # Assert
        assert cancelled.status == BookingStatus.CANCELLED
        assert cancelled.cancellation_reason == '客户要求'
```

**测试配置** (`conftest.py`)：

```python
# tests/conftest.py

import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient

# 配置pytest-asyncio
pytest_plugins = ('pytest_asyncio',)

@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环。"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """创建异步HTTP客户端。"""
    async with AsyncClient(base_url="http://localhost:8000") as client:
        yield client

@pytest.fixture
async def db_session():
    """创建数据库会话。"""
    from app.db.session import SessionLocal
    session = SessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
```

### 2. 前端单元测试

**测试框架**：Jest + React Testing Library + MSW (Mock Service Worker)

**目录结构**：

```
frontend/
├── src/
│   ├── components/
│   ├── hooks/
│   ├── services/
│   └── utils/
└── tests/              # 测试目录
    ├── __mocks__/      # 模拟数据
    ├── unit/
    │   ├── components/
    │   ├── hooks/
    │   └── utils/
    └── integration/
```

**测试示例**：

```typescript
// tests/unit/components/BookingCard.test.tsx

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BookingCard } from '../../../src/components/BookingCard';
import { BookingStatus } from '../../../src/types/booking';

// 模拟数据
const mockBooking = {
  id: 'booking-001',
  customerName: '张三',
  phone: '13800138000',
  roomId: 'room-001',
  roomName: '标准间A',
  checkIn: '2024-03-15',
  checkOut: '2024-03-17',
  status: BookingStatus.CONFIRMED,
  totalAmount: 596.00,
};

describe('BookingCard', () => {
  const mockOnCancel = jest.fn();
  const mockOnViewDetails = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('应该正确渲染预订信息', () => {
    render(
      <BookingCard
        booking={mockBooking}
        onCancel={mockOnCancel}
        onViewDetails={mockOnViewDetails}
      />
    );

    // 验证基本信息显示
    expect(screen.getByText('预订 #booking-001')).toBeInTheDocument();
    expect(screen.getByText('张三')).toBeInTheDocument();
    expect(screen.getByText('标准间A')).toBeInTheDocument();
    expect(screen.getByText('¥596.00')).toBeInTheDocument();
  });

  it('应该在点击"查看详情"时调用回调', () => {
    render(
      <BookingCard
        booking={mockBooking}
        onCancel={mockOnCancel}
        onViewDetails={mockOnViewDetails}
      />
    );

    const viewButton = screen.getByText('查看详情');
    fireEvent.click(viewButton);

    expect(mockOnViewDetails).toHaveBeenCalledWith('booking-001');
    expect(mockOnViewDetails).toHaveBeenCalledTimes(1);
  });

  it('应该在已确认状态下显示"取消预订"按钮', () => {
    render(
      <BookingCard
        booking={mockBooking}
        onCancel={mockOnCancel}
        onViewDetails={mockOnViewDetails}
      />
    );

    expect(screen.getByText('取消预订')).toBeInTheDocument();
  });

  it('在待处理状态下应该显示"取消预订"按钮', () => {
    const pendingBooking = { ...mockBooking, status: BookingStatus.PENDING };
    render(
      <BookingCard
        booking={pendingBooking}
        onCancel={mockOnCancel}
        onViewDetails={mockOnViewDetails}
      />
    );

    expect(screen.getByText('取消预订')).toBeInTheDocument();
  });

  it('在已取消状态下不应该显示"取消预订"按钮', () => {
    const cancelledBooking = { ...mockBooking, status: BookingStatus.CANCELLED };
    render(
      <BookingCard
        booking={cancelledBooking}
        onCancel={mockOnCancel}
        onViewDetails={mockOnViewDetails}
      />
    );

    expect(screen.queryByText('取消预订')).not.toBeInTheDocument();
  });

  it('应该在点击"取消预订"时调用回调', () => {
    render(
      <BookingCard
        booking={mockBooking}
        onCancel={mockOnCancel}
        onViewDetails={mockOnViewDetails}
      />
    );

    const cancelButton = screen.getByText('取消预订');
    fireEvent.click(cancelButton);

    expect(mockOnCancel).toHaveBeenCalledWith('booking-001');
    expect(mockOnCancel).toHaveBeenCalledTimes(1);
  });
});

// Hook测试示例
// tests/unit/hooks/useBookings.test.tsx

import { renderHook, waitFor } from '@testing-library/react';
import { useBookings } from '../../../src/hooks/useBookings';
import { getBookings } from '../../../src/services/bookingApi';

// Mock API
jest.mock('../../../src/services/bookingApi');

describe('useBookings', () => {
  const mockBookings = [
    { id: '1', customerName: '张三', status: 'confirmed' },
    { id: '2', customerName: '李四', status: 'pending' },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('应该返回预订列表', async () => {
    (getBookings as jest.Mock).mockResolvedValue({ data: mockBookings });

    const { result } = renderHook(() => useBookings('customer-1'));

    // 初始状态
    expect(result.current.loading).toBe(true);
    expect(result.current.bookings).toEqual([]);

    // 等待加载完成
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.bookings).toEqual(mockBookings);
    expect(result.current.error).toBeNull();
  });

  it('应该处理错误', async () => {
    (getBookings as jest.Mock).mockRejectedValue(new Error('网络错误'));

    const { result } = renderHook(() => useBookings('customer-1'));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toBe('网络错误');
    expect(result.current.bookings).toEqual([]);
  });

  it('应该可以刷新数据', async () => {
    (getBookings as jest.Mock)
      .mockResolvedValueOnce({ data: mockBookings })
      .mockResolvedValueOnce({ data: [...mockBookings, { id: '3', customerName: '王五' }] });

    const { result } = renderHook(() => useBookings('customer-1'));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.bookings).toHaveLength(2);

    // 刷新
    result.current.refetch();

    await waitFor(() => {
      expect(result.current.bookings).toHaveLength(3);
    });
  });
});
```

---

## API测试规范

### API测试最佳实践

- [ ] **状态码验证**：验证返回正确的HTTP状态码
- [ ] **响应结构**：验证响应数据结构符合预期
- [ ] **错误处理**：验证错误情况下的响应
- [ ] **边界测试**：测试边界值和极限情况
- [ ] **认证测试**：测试认证和授权逻辑

```python
# ✅ API测试示例
# tests/integration/test_booking_api.py

import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_booking_success(async_client: AsyncClient, db_session):
    """测试成功创建预订。"""
    # Arrange
    booking_data = {
        'customer_name': '张三',
        'phone': '13800138000',
        'room_id': 'room-001',
        'check_in': '2024-03-15',
        'check_out': '2024-03-17',
    }
    
    # Act
    response = await async_client.post('/api/bookings', json=booking_data)
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data['id'] is not None
    assert data['customer_name'] == '张三'
    assert data['status'] == 'pending'
    assert data['total_amount'] > 0

@pytest.mark.asyncio
async def test_create_booking_invalid_phone(async_client: AsyncClient):
    """测试无效手机号应返回400错误。"""
    # Arrange
    booking_data = {
        'customer_name': '张三',
        'phone': 'invalid-phone',  # 无效手机号
        'room_id': 'room-001',
        'check_in': '2024-03-15',
        'check_out': '2024-03-17',
    }
    
    # Act
    response = await async_client.post('/api/bookings', json=booking_data)
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert 'phone' in data['detail'] or '手机号' in data['detail']

@pytest.mark.asyncio
async def test_create_booking_past_date(async_client: AsyncClient):
    """测试过去日期应返回400错误。"""
    # Arrange
    booking_data = {
        'customer_name': '张三',
        'phone': '13800138000',
        'room_id': 'room-001',
        'check_in': '2020-01-01',  # 过去日期
        'check_out': '2020-01-03',
    }
    
    # Act
    response = await async_client.post('/api/bookings', json=booking_data)
    
    # Assert
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_get_booking_not_found(async_client: AsyncClient):
    """测试获取不存在的预订应返回404。"""
    # Act
    response = await async_client.get('/api/bookings/non-existent-id')
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert '不存在' in data['detail'] or 'not found' in data['detail'].lower()

@pytest.mark.asyncio
async def test_cancel_booking_success(async_client: AsyncClient, db_session):
    """测试成功取消预订。"""
    # Arrange - 先创建一个