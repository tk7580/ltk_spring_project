
package com.ltk.springproject.service;

import java.util.List;
import com.ltk.springproject.entity.Work;
import org.springframework.stereotype.Service;
import com.ltk.springproject.repository.WorkRepository;

@Service
public class RecommendService {
    private final WorkRepository workRepository;
    public RecommendService(WorkRepository workRepository){
        this.workRepository = workRepository;
    }
    public List<Work> getPersonal(long memberId){
        return workRepository.findPersonalRecommendations(memberId);
    }
}
