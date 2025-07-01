
package com.ltk.springproject.repository;

import java.util.List;
import com.ltk.springproject.entity.Work;
import org.springframework.stereotype.Repository;
import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;

@Repository
public class WorkRepository {
    @PersistenceContext
    private EntityManager em;

    public List<Work> findPersonalRecommendations(long memberId){
        return em.createNativeQuery(
            """SELECT w.* FROM work w
            JOIN workGenre wg ON wg.workId=w.id
            WHERE wg.genreId IN (
                SELECT wg2.genreId FROM memberWatchedWork mww
                JOIN workGenre wg2 ON wg2.workId=mww.workId
                WHERE mww.memberId=:mid
                GROUP BY wg2.genreId ORDER BY COUNT(*) DESC LIMIT 3
            ) AND w.id NOT IN (SELECT workId FROM memberWatchedWork WHERE memberId=:mid)
            ORDER BY w.averageRating DESC LIMIT 10""", Work.class)
            .setParameter("mid", memberId)
            .getResultList();
    }
}
