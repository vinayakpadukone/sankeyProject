
import logging
logger = logging.getLogger(__name__)

def getSymptomsQuery_1(start_date, end_date, speciality):
    logger.info(f"in getSymptomsQuery_1:")
    logger.debug(f"{start_date}, {end_date}, {speciality}")

    query = f"select t1.Src Src, concat(\'D- \',t1.Trgt) Trgt, t1.Count `Count` from (select case when c.SymptomId=\"0\" then cleanupData(c.Complaint) else cleanupData(sd.SymptomName) end Src,cleanupData(sp.Diagnosis) Trgt, count(*) `Count` \
            from TBL_SimplePrescription sp \
            join TBL_Complaint c on sp.CaseId=c.CaseId \
            left join TBL_SymptomsDictionary sd on c.SymptomId=sd.SymptomsDictionaryId \
            left join TBL_Case cs on sp.CaseId=cs.CaseId \
            LEFT JOIN TBL_Doctor sshdoc ON cs.CompletedBy = sshdoc.DoctorId \
            where cs.CompletedTime between unix_timestamp('{start_date}') and unix_timestamp('{end_date}')+86399 and sshdoc.DocSpecalityId={speciality} \
            group by Src,Trgt \
            ) as t1 where Src!=\'\' and Trgt!=\'\' ;"

    return query

def get_medicine_by_diagnosis_list(start_date, end_date, diagnosis_list):
	logger.info(f"in get_medicine_by_diagnosis_list:")
	logger.debug(f"{start_date}, {end_date}, {diagnosis_list}")

	query = f"select concat(\'D- \',t2.Src) Src, t2.Trgt Trgt, t2.Count `Count` from \
                (select cleanupData(Diagnosis) Src, cleanupData(MedicineName) Trgt, count(*) `Count` \
                from TBL_SimplePrescription sp \
                left join TBL_Case cs on sp.CaseId=cs.CaseId \
                where cs.CompletedTime between unix_timestamp('{start_date}') and unix_timestamp('{end_date}')+86399 \
                group by Diagnosis,MedicineName) as t2 \
        where t2.Src!=\'\' and t2.Trgt!=\'\' \
        AND concat(\'D- \', t2.Src) IN {tuple(diagnosis_list)} ;"

	logger.debug(f"query: {query}")
	return query