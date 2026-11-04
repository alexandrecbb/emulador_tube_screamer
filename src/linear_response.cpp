#include "ts808/linear_response.hpp"
#include "ts808/stages.hpp"
#include <Eigen/LU>
#include <cmath>
#include <numbers>
namespace ts808 {
Status linear_response(const PreparedParameters& p,const Controls& c,const StateVector& dc,
    const NumericalSettings& settings,std::span<const double> frequencies,
    std::span<ComplexResponse> continuous,std::span<ComplexResponse> discrete) noexcept {
    if(continuous.size()!=frequencies.size()||discrete.size()!=frequencies.size())return failure(FailureReason::invalid_configuration,SolveStage::configuration);
    Evaluation evaluation;auto status=assemble(dc,0,{},p,c,settings,SolveMode::dc,evaluation);if(!status.ok)return status;
    Jacobian g=evaluation.jacobian,cap=Jacobian::Zero();
    const double omega=2*std::numbers::pi*p.opamp.GBW/p.opamp.A0;
    for(int z:{z_clip,z_tone}){
        // At a DC root f=0 the slew derivative is unity; preserve the actual law derivative.
        g.row(z)*=-1;cap(z,z)=1/omega;
    }
    for(const auto& element:p.capacitors){
        const int a=element.a,b=element.b;const double value=element.value;
        if(a>=0)cap(a,a)+=value;
        if(b>=0)cap(b,b)+=value;
        if(a>=0&&b>=0){cap(a,b)-=value;cap(b,a)-=value;}
    }
    using Matrix=Eigen::Matrix<ComplexResponse,31,31>;using Vector=Eigen::Matrix<ComplexResponse,31,1>;
    for(std::size_t k=0;k<frequencies.size();++k){
        const double f=frequencies[k];if(!std::isfinite(f)||f<=0||f>=settings.rate_Hz/2.)return failure(FailureReason::invalid_grid,SolveStage::linear);
        for(int discrete_mode=0;discrete_mode<2;++discrete_mode){
            const double angular=discrete_mode?2*settings.rate_Hz*std::tan(std::numbers::pi*f/settings.rate_Hz):2*std::numbers::pi*f;
            Matrix a=g.cast<ComplexResponse>()+ComplexResponse(0,angular)*cap.cast<ComplexResponse>();Vector b=Vector::Zero();
            b[input]=1/p.resistors[0].value;
            for(int r=0;r<31;++r){const double row=voltage_row(r)?settings.voltage_scale_V:settings.current_scale_A;b[r]/=row;
                for(int col=0;col<31;++col)a(r,col)*=(is_current(col)?settings.current_scale_A:settings.voltage_scale_V)/row;}
            const Matrix original_a=a;const Vector original_b=b;
            if(settings.row_scaling==NumericalSettings::RowScaling::max_abs_after_physical)
                for(int r=0;r<31;++r){const double norm=a.row(r).cwiseAbs().maxCoeff();if(norm>0){a.row(r)/=norm;b[r]/=norm;}}
            Eigen::FullPivLU<Matrix> lu(a);lu.setThreshold(settings.pivot_epsilon_factor*31*std::numeric_limits<double>::epsilon());
            if(lu.rank()!=31)return failure(FailureReason::singular_boundary,SolveStage::linear);
            const double rcond=lu.rcond();if(!std::isfinite(rcond)||rcond<settings.minimum_rcond)return failure(FailureReason::ill_conditioned_boundary,SolveStage::linear);
            const Vector x=lu.solve(b);
            const double numerator=(original_a*x-original_b).lpNorm<Eigen::Infinity>();
            const double denominator=original_a.cwiseAbs().rowwise().sum().maxCoeff()*x.lpNorm<Eigen::Infinity>()+original_b.lpNorm<Eigen::Infinity>();
            if(!x.allFinite()||numerator/denominator>settings.maximum_backward_error)return failure(FailureReason::linear_backward_error,SolveStage::linear);
            (discrete_mode?discrete:continuous)[k]=x[output]*settings.voltage_scale_V;
        }
    }
    return {};
}

}
