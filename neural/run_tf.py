from dataset import load
from sklearn import cross_validation
import argparse
import tensorflow as tf

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--train", action="store_true", help="Train model with dataset otherwise load it.")
args = parser.parse_args()
# Load our dataset
X, y = load()

# Split dataset into train / test
X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.25)

# Initialize the variables (i.e. assign their default value)
init = tf.global_variables_initializer()

# Build fully connected DNN
with tf.Session() as session:
    # Run the initializer
    session.run(init)
    with tf.device('/gpu:0'):
        # Enable logging
        tf.logging.set_verbosity(tf.logging.INFO)
        # Create our classifier
        feature_columns = [tf.contrib.layers.real_valued_column("", dimension=1600)]
        classifier = tf.contrib.learn.DNNClassifier(feature_columns=feature_columns, hidden_units=[], n_classes=4, model_dir="model")
        if args.train:
            print('Training...')
            classifier.fit(X_train, y_train, steps=5000)
            print('Done !')

        # Evaluate
        test_count = 0
        error_count = 0
        print(X_test.shape)
        for i in zip(classifier.predict_proba(X_test), classifier.predict_classes(X_test), classifier.predict(X_test)):
            print("model.predict_proba", "--", i[0], "model.predict", "--",
                  i[2], "predict_clases", "--", i[1])
            print("Good :", i[2] - y_test[test_count] == 0)
            if i[2] - y_test[test_count] != 0:
                error_count += 1
            test_count += 1
        print('Total number of errors: %d / %d (%f)' % (error_count, test_count, error_count/test_count))
