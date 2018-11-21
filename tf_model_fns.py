# -*- coding: utf-8 -*-

import tensorflow as tf


# Hyper Parameters
class H_PARAMS:

    batch_size = 100
    learning_rate = 1e-3
    dropout_rate = 0.4
    n_classes = 2
    train_steps = 4000

    __doc__ += """
    Default Hyper-parameters: 
        batch_size = {0}
        learning_rate = {1}
        dropout_rate = {2}
        n_classes = {3}
        train_steps = {4}
    """.format(batch_size, learning_rate, dropout_rate, n_classes, train_steps)



def full_connect_model_fn(features, labels, mode, params: H_PARAMS):
    """Model function for Full Connect."""

    # Input Layer
    input_layer = tf.reshape(features["x"], [-1, 28, 50])

    # Trimmed layer
    trim = input_layer[:, :, :]

    # Dense Layer
    flat = tf.layers.flatten(trim)
    dense = tf.layers.dense(inputs=flat, units=1400,
                            activation=None)

    dropout = tf.layers.dropout(
        inputs=dense, rate=params.dropout_rate,
        training=(mode == tf.estimator.ModeKeys.TRAIN))

    # Logits Layer
    logits = tf.layers.dense(inputs=dropout,
                             units=params.n_classes)

    predictions = {
        # Generate predictions (for PREDICT and EVAL mode)
        "classes": tf.argmax(input=logits, axis=1),
        # Add `softmax_tensor` to the graph, It is used for PREDICT and by the
        # `logging_hook`.
        "probabilities": tf.nn.softmax(logits, name="softmax_tensor")
    }

    if mode == tf.estimator.ModeKeys.PREDICT:
        return tf.estimator.EstimatorSpec(mode=mode, predictions=predictions)

    # Calculate Loss (for both TRAIN and EVAL modes)
    loss = tf.losses.sparse_softmax_cross_entropy(labels=labels, logits=logits)

    # Configure the Training Op (for TRAIN mode)
    if mode == tf.estimator.ModeKeys.TRAIN:
        optimizer = tf.train.GradientDescentOptimizer(
            learning_rate=params.learning_rate,
        )
        train_op = optimizer.minimize(loss=loss,
                                      global_step=tf.train.get_global_step())
        return tf.estimator.EstimatorSpec(mode=mode, loss=loss,
                                          train_op=train_op)

    # Add evaluation metrics (for EVAL mode)
    eval_metric_ops = {
        "accuracy": tf.metrics.accuracy(
            labels=labels, predictions=predictions["classes"])}

    return tf.estimator.EstimatorSpec(
        mode=mode, loss=loss, eval_metric_ops=eval_metric_ops)


# used by estimator
def cnn_model_fn(features, labels, mode, params: H_PARAMS):
    """Model function for CNN."""

    # Input Layer
    input_layer = tf.reshape(features["x"], [-1, 50, 28, 1])
    # input_layer = input_layer[:, :, :, :]

    # Convolutional Layer #1
    conv1 = tf.layers.conv2d(
        inputs=input_layer, filters=16, kernel_size=5,
        padding="same", activation=tf.nn.relu)

    # Pooling Layer #1
    pool1 = tf.layers.max_pooling2d(inputs=conv1, pool_size=2, strides=2)

    # Convolutional Layers #2 and Pooling Layer #2
    conv2 = tf.layers.conv2d(
        inputs=pool1, filters=32, kernel_size=3,
        padding="same", activation=tf.nn.relu)
    pool2 = tf.layers.max_pooling2d(inputs=conv2, pool_size=2, strides=2)
    tf.logging.debug("shape of pool2: \n%s", pool2.shape)

    # Dense Layer
    pool2_flat = tf.layers.flatten(pool2)
    dense = tf.layers.dense(inputs=pool2_flat, units=12 * 7 * 32,
                            activation=tf.nn.sigmoid)
    dropout = tf.layers.dropout(
        inputs=dense, rate=params.dropout_rate,
        training=(mode == tf.estimator.ModeKeys.TRAIN))

    # Logits Layer
    logits = tf.layers.dense(inputs=dropout,
                             units=params.n_classes)

    predictions = {
        # Generate predictions (for PREDICT and EVAL mode)
        "classes": tf.argmax(input=logits, axis=1),
        # Add `softmax_tensor` to the graph, It is used for PREDICT and by the
        # `logging_hook`.
        "probabilities": tf.nn.softmax(logits, name="softmax_tensor")
    }

    if mode == tf.estimator.ModeKeys.PREDICT:
        return tf.estimator.EstimatorSpec(mode=mode, predictions=predictions)

    # Calculate Loss (for both TRAIN and EVAL modes)
    loss = tf.losses.sparse_softmax_cross_entropy(labels=labels, logits=logits)

    # Configure the Training Op (for TRAIN mode)
    if mode == tf.estimator.ModeKeys.TRAIN:
        optimizer = tf.train.AdamOptimizer(
            learning_rate=params.learning_rate,
        )
        train_op = optimizer.minimize(loss=loss,
                                      global_step=tf.train.get_global_step())
        return tf.estimator.EstimatorSpec(mode=mode, loss=loss,
                                          train_op=train_op)

    # Add evaluation metrics (for EVAL mode)
    eval_metric_ops = {
        "accuracy": tf.metrics.accuracy(
            labels=labels, predictions=predictions["classes"])}

    return tf.estimator.EstimatorSpec(
        mode=mode, loss=loss, eval_metric_ops=eval_metric_ops)


# used by estimator
def lstm_model_fn(features, labels, mode, params: H_PARAMS):
    """Model function for LSTM."""

    # Input Layer
    input_layer = tf.reshape(features["x"], [-1, 50, 28])

    # create 2 LSTMCells
    rnn_layers = [tf.nn.rnn_cell.LSTMCell(size) for size in (128, 256)]

    # create a RNN cell composed sequentially of a number of RNNCells
    multi_rnn_cell = tf.nn.rnn_cell.MultiRNNCell(rnn_layers)

    # 'outputs' is a tensor of shape [batch_size, max_time, 256]
    # 'state' is a N-tuple where N is the number of LSTMCells containing a
    # tf.contrib.rnn.LSTMStateTuple for each cell
    rnn_outputs, state = tf.nn.dynamic_rnn(cell=multi_rnn_cell,
                                           inputs=input_layer,
                                           dtype=tf.float32)
    # # Dense Layer
    rnn_outputs_flat = tf.layers.flatten(rnn_outputs)
    dense = tf.layers.dense(inputs=rnn_outputs_flat, units=1024,
                            activation=tf.nn.relu)
    dropout = tf.layers.dropout(
        inputs=dense, rate=params.dropout_rate,
        training=(mode == tf.estimator.ModeKeys.TRAIN))

    # Logits Layer
    logits = tf.layers.dense(inputs=dropout,
                             units=params.n_classes)

    predictions = {
        # Generate predictions (for PREDICT and EVAL mode)
        "classes": tf.argmax(input=logits, axis=1),
        # Add `softmax_tensor` to the graph, It is used for PREDICT and by the
        # `logging_hook`.
        "probabilities": tf.nn.softmax(logits, name="softmax_tensor")
    }

    if mode == tf.estimator.ModeKeys.PREDICT:
        return tf.estimator.EstimatorSpec(mode=mode, predictions=predictions)

    # Calculate Loss (for both TRAIN and EVAL modes)
    loss = tf.losses.sparse_softmax_cross_entropy(labels=labels, logits=logits)

    # Configure the Training Op (for TRAIN mode)
    if mode == tf.estimator.ModeKeys.TRAIN:
        optimizer = tf.train.GradientDescentOptimizer(
            learning_rate=params.learning_rate,
        )
        train_op = optimizer.minimize(loss=loss,
                                      global_step=tf.train.get_global_step())
        return tf.estimator.EstimatorSpec(mode=mode, loss=loss,
                                          train_op=train_op)

    # Add evaluation metrics (for EVAL mode)
    eval_metric_ops = {
        "accuracy": tf.metrics.accuracy(
            labels=labels, predictions=predictions["classes"])}

    return tf.estimator.EstimatorSpec(
        mode=mode, loss=loss, eval_metric_ops=eval_metric_ops)
