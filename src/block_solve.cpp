#include "ts808/block_solve.hpp"
#include <Eigen/LU>
#include <cmath>
namespace ts808 {
namespace {
void scale(const Jacobian& j,const Residual& rhs,const NumericalSettings& s,Jacobian& a,Residual& b) noexcept {
    for(int r=0;r<31;++r){const double row=voltage_row(r)?s.voltage_scale_V:s.current_scale_A;
        b[r]=rhs[r]/row;
        for(int c=0;c<31;++c)a(r,c)=j(r,c)*(is_current(c)?s.current_scale_A:s.voltage_scale_V)/row;}
}
void equilibrate(Jacobian& a,Residual& b,const NumericalSettings& s) noexcept {
    if(s.row_scaling==NumericalSettings::RowScaling::physical_only)return;
    for(int r=0;r<31;++r){const double norm=a.row(r).cwiseAbs().maxCoeff();
        if(norm>0&&std::isfinite(norm)){a.row(r)/=norm;b[r]/=norm;}}
}
template<int N> Status factor(const Eigen::Matrix<double,N,N>& a,const NumericalSettings& s,
    Eigen::FullPivLU<Eigen::Matrix<double,N,N>>& lu,int block) noexcept {
    if(!a.allFinite())return failure(FailureReason::nonfinite_trial,SolveStage::linear);
    lu.compute(a);lu.setThreshold(s.pivot_epsilon_factor*N*std::numeric_limits<double>::epsilon());
    Status status;status.diagnostics.block=block;status.diagnostics.rank=static_cast<int>(lu.rank());
    const bool boundary=block==4;
    if(lu.rank()!=N){status.ok=false;status.diagnostics.reason=boundary?FailureReason::singular_boundary:FailureReason::singular_internal;}
    else {const double rcond=lu.rcond();status.diagnostics.rcond={rcond,std::isfinite(rcond)};
        if(!std::isfinite(rcond)||rcond<s.minimum_rcond){status.ok=false;status.diagnostics.reason=boundary?FailureReason::ill_conditioned_boundary:FailureReason::ill_conditioned_internal;}}
    status.diagnostics.stage=SolveStage::linear;return status;
}
Status finish(const Jacobian& a,const Residual& b,const NumericalSettings& s,StateVector& scaled,StateVector& result) noexcept {
    const double numerator=(a*scaled-b).lpNorm<Eigen::Infinity>();
    const double denom=a.cwiseAbs().rowwise().sum().maxCoeff()*scaled.lpNorm<Eigen::Infinity>()+b.lpNorm<Eigen::Infinity>();
    const double eta=denom==0?(numerator==0?0:std::numeric_limits<double>::infinity()):numerator/denom;
    Status status;status.diagnostics.backward_error={eta,std::isfinite(eta)};
    if(!scaled.allFinite()||!std::isfinite(eta)||eta>s.maximum_backward_error){status.ok=false;status.diagnostics.reason=FailureReason::linear_backward_error;status.diagnostics.stage=SolveStage::linear;return status;}
    for(int i=0;i<31;++i)result[i]=scaled[i]*(is_current(i)?s.current_scale_A:s.voltage_scale_V);
    return status;
}
template<int N,int Start> struct Interior {
    Eigen::Matrix<double,N,5> ab;
    Eigen::Matrix<double,5,N> ba;
    Eigen::Matrix<double,N,1> bi;
    Eigen::FullPivLU<Eigen::Matrix<double,N,N>> lu;
    Status eliminate(const Jacobian& a,const Residual& b,const NumericalSettings& s,
        Eigen::Matrix<double,5,5>& schur,Eigen::Matrix<double,5,1>& rhs,int block) noexcept {
        const Eigen::Matrix<double,N,N> ii=a.template block<N,N>(Start,Start);
        auto status=factor<N>(ii,s,lu,block);if(!status.ok)return status;
        ab=a.template block<N,5>(Start,26);ba=a.template block<5,N>(26,Start);bi=b.template segment<N>(Start);
        schur.noalias()-=ba*lu.solve(ab);rhs.noalias()-=ba*lu.solve(bi);return status;
    }
    void recover(StateVector& x) noexcept {x.template segment<N>(Start)=lu.solve((bi-ab*x.template tail<5>()).eval());}
};
}
Status block_solve(const Jacobian& j,const Residual& rhs,const NumericalSettings& s,StateVector& result) noexcept {
    Jacobian a;Residual b;scale(j,rhs,s,a,b);
    if(!a.allFinite()||!b.allFinite())return failure(FailureReason::nonfinite_trial,SolveStage::linear);
    const Jacobian original_a=a;const Residual original_b=b;equilibrate(a,b,s);
    Eigen::Matrix<double,5,5> schur=a.bottomRightCorner<5,5>();Eigen::Matrix<double,5,1> br=b.tail<5>();
    Interior<4,0> in;Interior<6,4> clip;Interior<11,10> tone;Interior<5,21> out;
    auto status=in.eliminate(a,b,s,schur,br,0);if(!status.ok)return status;
    status=clip.eliminate(a,b,s,schur,br,1);if(!status.ok)return status;
    status=tone.eliminate(a,b,s,schur,br,2);if(!status.ok)return status;
    status=out.eliminate(a,b,s,schur,br,3);if(!status.ok)return status;
    Eigen::FullPivLU<Eigen::Matrix<double,5,5>> lu;status=factor<5>(schur,s,lu,4);if(!status.ok)return status;
    StateVector x;x.tail<5>()=lu.solve(br);in.recover(x);clip.recover(x);tone.recover(x);out.recover(x);
    auto done=finish(original_a,original_b,s,x,result);done.diagnostics.rcond=status.diagnostics.rcond;return done;
}
Status full_solve(const Jacobian& j,const Residual& rhs,const NumericalSettings& s,StateVector& result) noexcept {
    Jacobian a;Residual b;scale(j,rhs,s,a,b);if(!b.allFinite())return failure(FailureReason::nonfinite_trial,SolveStage::linear);
    const Jacobian original_a=a;const Residual original_b=b;equilibrate(a,b,s);
    Eigen::FullPivLU<Jacobian> lu;auto status=factor<31>(a,s,lu,5);if(!status.ok)return status;
    StateVector x=lu.solve(b);return finish(original_a,original_b,s,x,result);
}
}
