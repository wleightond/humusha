
# allinstances:
# 	cat test_ontology.clif | ./bin/find_cdp_instances > ./instances/cdp_instances;
# 	cat test_ontology.clif | ./bin/find_cop_instances > ./instances/cop_instances;
# 	cat test_ontology.clif | ./bin/find_pcop_instances > ./instances/pcop_instances;
# 	cat test_ontology.clif | ./bin/find_qdp_instances > ./instances/qdp_instances;
# 	cat test_ontology.clif | ./bin/find_rr_instances > ./instances/rr_instances;

# allsubs:
# 	cat ./instances/cdp_instances 	| ./find_patterns.py > ./substitutions/cdp_substitutions
# 	cat ./instances/cop_instances 	| ./find_patterns.py > ./substitutions/cop_substitutions
# 	cat ./instances/pcop_instances 	| ./find_patterns.py > ./substitutions/pcop_substitutions
# 	cat ./instances/qdp_instances 	| ./find_patterns.py > ./substitutions/qdp_substitutions
# 	cat ./instances/rr_instances 	| ./find_patterns.py > ./substitutions/rr_substitutions

# testrr:
# 	cat test_ontology.clif | ./bin/find_rr_instances | ./find_patterns.py

utils:
	cd build/utils;	cabal build; cd ../../
	cp $$(find . -name utils-0.1.0.0)/x/prep_onto/build/prep_onto/prep_onto ./prep_onto
	cp $$(find . -name utils-0.1.0.0)/x/simple_parse/build/simple_parse/simple_parse ./simple_parse

finders:
	./humusha build-instance-finders

test-patts:
	for i in {cdp,cop,cra_e,pcop,qdp,rr}; do ./humusha run-all $$i ./test_files/test_$$i.clif; done

test-reals:
	for file in {DMOP,MDMOP,MNaive_animal_ontology2,MOntoDerm_5.3,MSEGOv3,MSceneOntology,MScene_rr,PhysicalEntity,SceneOntology,SpacialAction}; do for i in {cdp,cop,cra_e,pcop,qdp,rr}; do ./humusha run-all $$i ./test_files/$$file.clif; done; done
	for i in {cdp,cop,cra_e,pcop,qdp,rr}; do ./humusha run-all $$i ./test_files/test_ontology.clif; done

test: test-patts test-reals

all: utils finders test
