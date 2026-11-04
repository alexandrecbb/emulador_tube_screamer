#include "ts808/model.hpp"
#include <catch2/catch_test_macros.hpp>
#include <atomic>
#include <cstdlib>
#include <new>

namespace { std::atomic<bool> guarded{false};std::atomic<unsigned> allocations{0},deallocations{0}; }
void* operator new(std::size_t n){if(guarded)++allocations;if(void* p=std::malloc(n?n:1))return p;throw std::bad_alloc();}
void* operator new[](std::size_t n){return ::operator new(n);}
void operator delete(void* p) noexcept {if(p&&guarded)++deallocations;std::free(p);}
void operator delete[](void* p) noexcept {::operator delete(p);}
void operator delete(void* p,std::size_t) noexcept {::operator delete(p);}
void operator delete[](void* p,std::size_t) noexcept {::operator delete(p);}
void* operator new(std::size_t n,std::align_val_t a){if(guarded)++allocations;void* p=nullptr;if(posix_memalign(&p,static_cast<std::size_t>(a),n?n:1))throw std::bad_alloc();return p;}
void* operator new[](std::size_t n,std::align_val_t a){return ::operator new(n,a);}
void operator delete(void* p,std::align_val_t) noexcept {::operator delete(p);}
void operator delete[](void* p,std::align_val_t) noexcept {::operator delete(p);}
void operator delete(void* p,std::size_t,std::align_val_t) noexcept {::operator delete(p);}
void operator delete[](void* p,std::size_t,std::align_val_t) noexcept {::operator delete(p);}

TEST_CASE("Prepared first step, repeated steps and nonfinite failure allocate nothing") {
    ts808::Model model;REQUIRE(model.prepare({}, {0,.5,.5}, {}).ok);REQUIRE(model.initialize_dc(0).status.ok);
    allocations=deallocations=0;
#ifdef EIGEN_RUNTIME_NO_MALLOC
    Eigen::internal::set_is_malloc_allowed(false);
#endif
    guarded=true;bool ok=true;ts808::StepResult last;int failed_at=-1;
    for(int i=0;i<100;++i){last=model.advance(i<5?i*1e-5:0);if(!last.status.ok){ok=false;failed_at=i;break;}}
    const bool failed=!model.advance(std::numeric_limits<double>::quiet_NaN()).status.ok;
    guarded=false;
#ifdef EIGEN_RUNTIME_NO_MALLOC
    Eigen::internal::set_is_malloc_allowed(true);
#endif
    INFO("failed_at "<<failed_at<<" reason "<<static_cast<int>(last.status.diagnostics.reason)<<" residual "<<last.status.diagnostics.residual_norm.value<<" increment "<<last.status.diagnostics.increment_norm.value);REQUIRE(ok);REQUIRE(failed);REQUIRE(allocations==0);REQUIRE(deallocations==0);
}
