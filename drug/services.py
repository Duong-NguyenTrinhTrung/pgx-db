from interaction.models import Interaction
from .models import Drug
from protein.models import Protein
from django.http import JsonResponse
from disease.models import DrugDiseaseStudy, Disease


class DrugNetworkGetDataService(object):
    def __init__(self, drug):
        self.drug = drug
        
    def get_drug_network_data(self) -> dict:
        return {
            'general_data': self.get_general_data(),
            'drug_data': self.get_drug_data(),
            'interaction_data': self.get_interaction_data(),
            'protein_data': self.get_protein_data(),
        }

    def get_general_data(self) -> list[dict]:
        drug_protein_interactions = Interaction.objects.filter(drug_bankID=self.drug.drug_bankID)
        drug_disease_interactions = DrugDiseaseStudy.objects.filter(drug_bankID=self.drug.drug_bankID)
        general_data = []
        for t1 in drug_protein_interactions: # loop through all interactions
                if len(drug_disease_interactions) != 0: 
                    for t2 in drug_disease_interactions:
                        interaction_info = {
                            "interaction_id": t1.interaction_id,
                            "interaction_type": t1.interaction_type,
                            "pubmed_ids": t1.pubmed_ids,
                        }
                        drug_info = {
                            "drugbank_id": t1.drug_bankID.drug_bankID,
                            "drug_name": t1.drug_bankID.name,
                            "drugtype": t1.drug_bankID.drugtype.type_detail,
                            "Drug_status": t1.drug_bankID.Clinical_status,
                        }
                        protein_info = {
                            "protein": t1.uniprot_ID.uniprot_ID,
                            "protein_name": t1.uniprot_ID.protein_name,
                            "Protein_Class": t1.uniprot_ID.Protein_class,
                            "gene_name": t1.uniprot_ID.genename,
                        }
                        disease_info = {
                            "Phase": t2.clinical_trial,
                            "Disease_name": t2.disease_name.disease_name,
                            "Disease_class": t2.disease_name.disease_class,
                        }
                        
                        interaction_data = {
                            **interaction_info,
                            **drug_info,
                            **protein_info,
                            **disease_info,
                        }
                        general_data.append(interaction_data)
                else:
                    interaction_info = {
                            "interaction_id": t1.interaction_id,
                            "interaction_type": t1.interaction_type,
                            "pubmed_ids": t1.pubmed_ids,
                        }
                    drug_info = {
                        "drugbank_id": t1.drug_bankID.drug_bankID,
                        "drug_name": t1.drug_bankID.name,
                        "drugtype": t1.drug_bankID.drugtype.type_detail,
                        "Drug_status": t1.drug_bankID.Clinical_status,
                    }
                    protein_info = {
                        "protein": t1.uniprot_ID.uniprot_ID,
                        "protein_name": t1.uniprot_ID.protein_name,
                        "Protein_Class": t1.uniprot_ID.Protein_class,
                        "gene_name": t1.uniprot_ID.genename,
                    }
                    disease_info = {
                        "Phase": "",
                        "Disease_name": "",
                        "Disease_class": "",
                    }
                    
                    interaction_data = {
                        **interaction_info,
                        **drug_info,
                        **protein_info,
                        **disease_info,
                    }
                    general_data.append(interaction_data)
        return general_data

    def get_drug_data(self) -> list[dict]:
        drug_dict = {
            "drug_bankID": self.drug.drug_bankID,
            "drugtype": self.drug.drugtype.type_detail,
            "name": self.drug.name,
            "groups": self.drug.groups.group_detail,
            "categories": self.drug.categories.category_detail,
            "description": self.drug.description,
            "aliases": self.drug.aliases,
            "superclass": self.drug.superclass.superclass_detail,
            "classname": self.drug.classname.class_detail,
            "subclass": self.drug.subclass.subclass_detail,
            "direct_parent": self.drug.direct_parent.parent_detail,
            "indication": self.drug.indication,
            "pharmacodynamics": self.drug.pharmacodynamics,
            "moa": self.drug.moa,
            "absorption": self.drug.absorption,
            "toxicity": self.drug.toxicity,
            "halflife": self.drug.halflife,
            "distribution_volume": self.drug.distribution_volume,
            "protein_binding": self.drug.protein_binding,
            "dosages": self.drug.dosages,
            "properties": self.drug.properties,
            "chEMBL": self.drug.chEMBL.chembl_detail,
            "pubChemCompound": self.drug.pubChemCompound.compound_detail,
            "pubChemSubstance": self.drug.pubChemSubstance.pubchemblsubstance_detail,
            "Clinical_status": self.drug.Clinical_status,
        }
        return [drug_dict]

    def get_interaction_data(self) -> list[dict]:
        interactions = Interaction.objects.filter(drug_bankID=self.drug.drug_bankID)
        interaction_data = []
        for interaction in interactions:
            interaction_dict = {
                "interaction_id": interaction.interaction_id,
                "drug_bankID": interaction.drug_bankID.drug_bankID,
                "uniprot_ID": interaction.uniprot_ID.uniprot_ID,
                "gene_name": interaction.uniprot_ID.genename,
                "actions": interaction.actions,
                "known_action": interaction.known_action,
                "interaction_type": interaction.interaction_type,
                "pubmed_ids": interaction.pubmed_ids,
            }
            interaction_data.append(interaction_dict)
        return interaction_data
    
    def get_protein_data(self) -> list[dict]:
        uniprot_IDs = Interaction.objects.filter(drug_bankID=self.drug.drug_bankID).values_list('uniprot_ID',flat=True)
        proteins = Protein.objects.filter(uniprot_ID__in=uniprot_IDs)
        protein_data = []
        for protein in proteins:
            protein_dict = {
                "uniprot_ID": protein.uniprot_ID,
                "gene_name": protein.genename,
                "geneID": protein.geneID,
                "entry_name": protein.entry_name,
                "protein_name": protein.protein_name,
                "sequence": protein.sequence,
                "af_pdb": protein.af_pdb,
                "Protein_class": protein.Protein_class,
            }
            protein_data.append(protein_dict)
        return protein_data
    
class DrugsNetworkGetDataService:
    def __init__(self, drug_bank_ids):
        self.drug_bank_ids = drug_bank_ids

    def get_general_data(self) -> list[dict]:
        """
        Get general data for drugs network
        """
        drug_protein_interactions = Interaction.objects.filter(drug_bankID__in=self.drug_bank_ids).distinct()
        general_data = []
        for t1 in drug_protein_interactions:
                drug_bank_id = t1.drug_bankID
                drug_disease_interactions = DrugDiseaseStudy.objects.filter(drug_bankID=drug_bank_id).distinct()
                if len(drug_disease_interactions) != 0:
                    for t2 in drug_disease_interactions:
                        interaction_info = {
                            "interaction_id": t1.interaction_id,
                            "interaction_type": t1.interaction_type,
                            "pubmed_ids": t1.pubmed_ids,
                        }
                        drug_info = {
                            "drugbank_id": t1.drug_bankID.drug_bankID,
                            "drug_name": t1.drug_bankID.name,
                            "drugtype": t1.drug_bankID.drugtype.type_detail,
                            "Drug_status": t1.drug_bankID.Clinical_status,
                        }
                        protein_info = {
                            "protein": t1.uniprot_ID.uniprot_ID,
                            "protein_name": t1.uniprot_ID.protein_name,
                            "Protein_Class": t1.uniprot_ID.Protein_class,
                            "gene_name": t1.uniprot_ID.genename,
                        }
                        disease_info = {
                            "Phase": t2.clinical_trial,
                            "Disease_name": t2.disease_name.disease_name,
                            "Disease_class": t2.disease_name.disease_class,
                        }
                        
                        interaction_data = {
                            **interaction_info,
                            **drug_info,
                            **protein_info,
                            **disease_info,
                        }
                        general_data.append(interaction_data)
                else:
                    interaction_info = {
                            "interaction_id": t1.interaction_id,
                            "interaction_type": t1.interaction_type,
                            "pubmed_ids": t1.pubmed_ids,
                        }
                    drug_info = {
                        "drugbank_id": t1.drug_bankID.drug_bankID,
                        "drug_name": t1.drug_bankID.name,
                        "drugtype": t1.drug_bankID.drugtype.type_detail,
                        "Drug_status": t1.drug_bankID.Clinical_status,
                    }
                    protein_info = {
                        "protein": t1.uniprot_ID.uniprot_ID,
                        "protein_name": t1.uniprot_ID.protein_name,
                        "Protein_Class": t1.uniprot_ID.Protein_class,
                        "gene_name": t1.uniprot_ID.genename,
                    }
                    disease_info = {
                        "Phase": "",
                        "Disease_name": "",
                        "Disease_class": "",
                    }
                    
                    interaction_data = {
                        **interaction_info,
                        **drug_info,
                        **protein_info,
                        **disease_info,
                    }
                    general_data.append(interaction_data)
        return general_data

    def get_drug_data(self) -> list[dict]:
        """
        Get drug data for drugs network
        """
        drugs = Drug.objects.filter(drug_bankID__in=self.drug_bank_ids)
        drug_data = []
        for drug in drugs:
            drug_dict = {
                "drug_bankID": drug.drug_bankID,
                "drugtype": drug.drugtype.type_detail,
                "name": drug.name,
                "groups": drug.groups.group_detail,
                "categories": drug.categories.category_detail,
                "description": drug.description,
                "aliases": drug.aliases,
                "superclass": drug.superclass.superclass_detail,
                "classname": drug.classname.class_detail,
                "subclass": drug.subclass.subclass_detail,
                "direct_parent": drug.direct_parent.parent_detail,
                "indication": drug.indication,
                "pharmacodynamics": drug.pharmacodynamics,
                "moa": drug.moa,
                "absorption": drug.absorption,
                "toxicity": drug.toxicity,
                "halflife": drug.halflife,
                "distribution_volume": drug.distribution_volume,
                "protein_binding": drug.protein_binding,
                "dosages": drug.dosages,
                "properties": drug.properties,
                "chEMBL": drug.chEMBL.chembl_detail,
                "pubChemCompound": drug.pubChemCompound.compound_detail,
                "pubChemSubstance": drug.pubChemSubstance.pubchemblsubstance_detail,
                "Clinical_status": drug.Clinical_status,
            }
            drug_data.append(drug)
        return drug_data

    def get_drug_data2(self) -> list[dict]:
        """
        Get drug data for drugs network
        """
        drugs = Drug.objects.filter(drug_bankID__in=self.drug_bank_ids)
        drug_data = []
        for drug in drugs:
            drug_dict = {
                "drug_bankID": drug.drug_bankID,
                "drugtype": drug.drugtype.type_detail,
                "name": drug.name,
                "groups": drug.groups.group_detail,
                "categories": drug.categories.category_detail,
                "description": drug.description,
                "aliases": drug.aliases,
                "superclass": drug.superclass.superclass_detail,
                "classname": drug.classname.class_detail,
                "subclass": drug.subclass.subclass_detail,
                "direct_parent": drug.direct_parent.parent_detail,
                "indication": drug.indication,
                "pharmacodynamics": drug.pharmacodynamics,
                "moa": drug.moa,
                "absorption": drug.absorption,
                "toxicity": drug.toxicity,
                "halflife": drug.halflife,
                "distribution_volume": drug.distribution_volume,
                "protein_binding": drug.protein_binding,
                "dosages": drug.dosages,
                "properties": drug.properties,
                "chEMBL": drug.chEMBL.chembl_detail,
                "pubChemCompound": drug.pubChemCompound.compound_detail,
                "pubChemSubstance": drug.pubChemSubstance.pubchemblsubstance_detail,
                "Clinical_status": drug.Clinical_status,
            }
            drug_data.append(drug_dict)
        return drug_data

    def get_interaction_data(self) -> list[dict]:
        """
        Get interaction data for drugs network
        """
        interactions = Interaction.objects.filter(drug_bankID__in=self.drug_bank_ids)
        interaction_data = []
        for interaction in interactions:
            interaction_dict = {
                "interaction_id": interaction.interaction_id,
                "drug_bankID": interaction.drug_bankID.drug_bankID,
                "uniprot_ID": interaction.uniprot_ID.uniprot_ID,
                "gene_name": interaction.uniprot_ID.genename,
                "actions": interaction.actions,
                "known_action": interaction.known_action,
                "interaction_type": interaction.interaction_type,
                "pubmed_ids": interaction.pubmed_ids,
            }
            interaction_data.append(interaction_dict)
        return interaction_data

    def get_protein_data(self) -> list[dict]:
        """
        Get protein data for drugs network
        """
        uniprot_IDs = Interaction.objects.filter(drug_bankID__in=self.drug_bank_ids).values_list('uniprot_ID',flat=True)
        proteins = Protein.objects.filter(uniprot_ID__in=uniprot_IDs)
        protein_data = []
        for protein in proteins:
            protein_dict = {
                "uniprot_ID": protein.uniprot_ID,
                "gene_name": protein.genename,
                "geneID": protein.geneID,
                "entry_name": protein.entry_name,
                "protein_name": protein.protein_name,
                "sequence": protein.sequence,
                "af_pdb": protein.af_pdb,
                "Protein_class": protein.Protein_class,
            }
            protein_data.append(protein_dict)
        return protein_data
