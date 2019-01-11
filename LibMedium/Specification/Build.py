from LibMedium.Specification.Builders.Python import PythonBuilder
from LibMedium.Specification.Model import SpecificationModel

import os

BUILDERS = {
    "python3": PythonBuilder
}


if __name__ == "__main__":
    import sys
    if(len(sys.argv) != 4):
        print("Expected three arguments:")
        print("\tspec_file language output_dir")
        print("\nSupported languages:")
        for key in BUILDERS.keys():
            print("\t%s" % key)

        print("\n")
        exit()

    # We have all the values
    in_file = sys.argv[1]
    language = sys.argv[2]
    out_dir = sys.argv[3]

    f = open(in_file)
    builder_class = BUILDERS[language]
    
    model = SpecificationModel(f.read())
    f.close()

    if(os.path.exists(out_dir)):
        raise Exception("Output path already exists")

    os.mkdir(out_dir)

    builder = builder_class(model.namespace, model.class_name, out_dir)

    builder.create_interface(model.models, model.exceptions, model.methods, model.events)

    print("\n\nComplete!")
    exit()
