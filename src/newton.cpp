#include "ts808/newton.hpp"
#include "ts808/block_solve.hpp"
#include <cmath>
namespace ts808 {
StateVector dc_initial_guess() noexcept {
    StateVector x=StateVector::Constant(4.5);
    x[input]=x[tone_rc]=x[output]=x[z_clip]=x[z_tone]=0;
    x[input_emitter]=x[output_emitter]=x[output_cap]=3.85;
    for(int i=0;i<31;++i)if(is_current(i))x[i]=0;
    return x;
}
Status newton(StateVector& x,double source,const CommittedHistory& h,const PreparedParameters& p,
    const Controls& c,const NumericalSettings& s,SolveMode mode) noexcept {
    const auto stage=mode==SolveMode::dc?SolveStage::dc:SolveStage::transient;
    const auto cap=mode==SolveMode::dc?s.max_newton_dc:s.max_newton_transient;
    double increment_norm=0;std::uint32_t total_trials=0;
    for(std::uint32_t iteration=0;;++iteration){
        Evaluation a;auto status=assemble(x,source,h,p,c,s,mode,a);status.diagnostics.stage=stage;
        status.diagnostics.iterations=iteration;status.diagnostics.trials=total_trials;if(!status.ok)return status;
        Residual weights;
        for(int i=0;i<31;++i)weights[i]=1/((voltage_row(i)?s.atol_voltage_V:s.atol_current_A)+s.rtol_residual*a.contributions[i]);
        const Residual wr=(weights.array()*a.residual.array()).matrix();const double norm=wr.lpNorm<Eigen::Infinity>();
        status.diagnostics.residual_norm={norm,true};status.diagnostics.increment_norm={increment_norm,true};
        if(norm<=1&&increment_norm<=1)return status;
        if(iteration>=cap){status.ok=false;status.diagnostics.reason=FailureReason::newton_budget_exhausted;return status;}
        StateVector delta;auto linear=block_solve(a.jacobian,-a.residual,s,delta);
        if(!linear.ok){linear.diagnostics.stage=stage;linear.diagnostics.iterations=iteration;return linear;}
        const Residual direction=(weights.array()*(a.jacobian*delta).array()).matrix();
        const double slope=wr.dot(direction), merit=.5*wr.squaredNorm();
        if(!std::isfinite(slope)||slope>=0){status.ok=false;status.diagnostics.reason=FailureReason::non_descent_direction;return status;}
        bool accepted=false;StateVector next;std::uint32_t trial=0;
        for(;trial<s.max_line_search;++trial){
            ++total_trials;
            const double alpha=std::ldexp(1.,-static_cast<int>(trial));next=x+alpha*delta;
            Evaluation t;const auto ts=assemble(next,source,h,p,c,s,mode,t);
            if(!ts.ok)continue;
            // A converged candidate terminates the root solve before further merit search.
            // Both tests use the actual representable candidate and its actual increment.
            double trial_residual=0, trial_increment=0;
            for(int i=0;i<31;++i){
                const double row_scale=(voltage_row(i)?s.atol_voltage_V:s.atol_current_A)+s.rtol_residual*t.contributions[i];
                const double x_scale=(is_current(i)?s.atol_increment_current_A:s.atol_increment_voltage_V)+
                    s.rtol_increment*std::max(std::abs(x[i]),std::abs(next[i]));
                trial_residual=std::max(trial_residual,std::abs(t.residual[i])/row_scale);
                trial_increment=std::max(trial_increment,std::abs(next[i]-x[i])/x_scale);
            }
            if(trial_residual<=1&&trial_increment<=1){
                x=next;status.diagnostics.iterations=iteration+1;status.diagnostics.trials=total_trials;
                status.diagnostics.residual_norm={trial_residual,true};status.diagnostics.increment_norm={trial_increment,true};
                status.diagnostics.backward_error=linear.diagnostics.backward_error;return status;
            }
            const Residual wt=(weights.array()*t.residual.array()).matrix();
            if(.5*wt.squaredNorm()<=merit+s.armijo_c1*alpha*slope){accepted=true;break;}
        }
        if(!accepted){status.ok=false;status.diagnostics.reason=FailureReason::line_search_exhausted;status.diagnostics.trials=total_trials;return status;}
        increment_norm=0;
        for(int i=0;i<31;++i){const double scale=(is_current(i)?s.atol_increment_current_A:s.atol_increment_voltage_V)+
            s.rtol_increment*std::max(std::abs(x[i]),std::abs(next[i]));
            increment_norm=std::max(increment_norm,std::abs(next[i]-x[i])/scale);}
        x=next;
    }
}
}
