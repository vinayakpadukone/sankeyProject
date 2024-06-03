import logging
from app.database.queries import *

logger = logging.getLogger(__name__)

class CaseService:
    def __init__(self, case_repository):
        logger.info(f"__init__:")
        logger.debug(f"{self}, {case_repository}")
        
        self.case_repository = case_repository

    def get_symptoms_by_case_speciality_and_bw_dates(self, start_date, end_date, speciality):
        logger.info(f"in get_symptoms_by_case_speciality_and_bw_dates:")
        logger.debug(f"{self}, {start_date}, {end_date}, {speciality}")

        query = getSymptomsQuery_1(start_date, end_date, speciality)
        return self.case_repository.execute(query)

    def get_symptoms_caseid_by_case_speciality_and_bw_dates(self, start_date, end_date, speciality, symptoms):
        logger.info(f"in get_symptoms_caseid_by_case_speciality_and_bw_dates:")
        logger.debug(f"{self}, {start_date}, {end_date}, {speciality}")

        query = f"SELECT DISTINCT t1.case_id AS CaseId\
            FROM ( \
                SELECT CASE WHEN c.SymptomId=\"0\" THEN cleanupData(c.Complaint) ELSE cleanupData(sd.SymptomName) END Src, sp.CaseId case_id \
                FROM TBL_SimplePrescription sp \
                JOIN TBL_Complaint c ON sp.CaseId=c.CaseId \
                LEFT JOIN TBL_SymptomsDictionary sd ON c.SymptomId=sd.SymptomsDictionaryId \
                LEFT JOIN TBL_Case cs ON sp.CaseId=cs.CaseId \
                LEFT JOIN TBL_Doctor sshdoc ON cs.CompletedBy = sshdoc.DoctorId \
                WHERE cs.CompletedTime BETWEEN UNIX_TIMESTAMP('{start_date}') AND UNIX_TIMESTAMP('{end_date}')+86399 AND sshdoc.DocSpecalityId={speciality} \
            ) AS t1 \
            WHERE t1.Src!='' \
            AND t1.Src LIKE '%{symptoms}%';"

        return self.case_repository.execute(query)

    def get_medicine_bw_dates_by_diagnosis_list(self, start_date, end_date, diagnosis_list):
        logger.info(f"in get_medicine_bw_dates_by_diagnosis_list:")
        logger.debug(f"{self}, {start_date}, {end_date}, {diagnosis_list}")

        query = get_medicine_by_diagnosis_list(start_date, end_date, diagnosis_list)
        return self.case_repository.execute(query)

    def get_medicine_bw_dates_by_caseid_list(self, start_date, end_date, caseid_list):
        logger.info(f"in get_medicine_bw_dates_by_diagnosis_list:")
        logger.debug(f"{self}, {start_date}, {end_date}, {caseid_list}")

        query = f"select concat('D- ',t2.Src) Src, t2.Trgt Trgt, t2.Count `Count` from \
                (select cleanupData(Diagnosis) Src, cleanupData(MedicineName) Trgt, count(*) `Count` \
                from TBL_SimplePrescription sp \
                left join TBL_Case cs on sp.CaseId=cs.CaseId \
                where cs.CompletedTime between unix_timestamp('{start_date}') and unix_timestamp('{end_date}')+86399 \
                AND sp.CaseId IN {tuple(caseid_list)} \
                group by Diagnosis,MedicineName) as t2 \
            where t2.Src!='' and t2.Trgt!='' ;"

        return self.case_repository.execute(query)


# Samples

class UserService:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    def get_user_by_id(self, user_id):
        return self.user_repository.get_user_by_id(user_id)


class ProductService:
    def __init__(self, product_repository):
        self.product_repository = product_repository

    def get_product_by_id(self, product_id):
        return self.product_repository.get_product_by_id(product_id)
