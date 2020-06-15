from datetime import datetime

# custom_aggregator=dict(
#     type='PPIAggregator',
#     nrof_neigh_per_batch=nrof_neigh_per_batch,
#     depth=depth,
#     aggregators_shape=[(100, 50), (100, 50)],
#     attention_shapes=[(100, 1), (100, 1)],
#     aggregator_type=dict(
#         type='MeanAggregator',
#         activation='leaky_relu',
#         attention_layer=dict(
#             type='GATLayer',
#             attention_mechanism=dict(
#                 type='SingleLayerMechanism'
#             ),
#             activation='leaky_relu'
#         )
#     )
# )

# custom_aggregator=dict(
#         type='PPIAggregator',
#         nrof_neigh_per_batch=10,
#         depth=2,
#         aggregators_shape=[(50, 50, 100, 50), (50, 50, 100, 50)],
#         attention_shapes=[(100, 1), (100, 1)],
#         aggregator_type=dict(
#             type='PoolAggregator',
#             activation='leaky_relu',
#             pool_op='reduce_max',
#             # attention_layer=None
#             attention_layer=dict(
#                 type='GATLayer',
#                 attention_mechanism=dict(
#                     type='SingleLayerMechanism'
#                 ),
#                 activation='leaky_relu'
#             )
#         )
#     )


# model settings
nrof_neigh_per_batch=25
depth=2
num_classes = 121

model = dict(
    type='GraphSAGE',
    in_shape=50,
    out_shape=num_classes,
    activation='sigmoid',
    custom_aggregator=dict(
        type='PPIAggregator',
        nrof_neigh_per_batch=nrof_neigh_per_batch,
        depth=2,
        aggregators_shape=[((None, nrof_neigh_per_batch, 50), 50, 100, 50),
                           ((None, nrof_neigh_per_batch, 50), 50, 100, 50)],
        attention_shapes=[(100, 1), (100, 1)],
        aggregator_type=dict(
            type='RNNAggregator',
            activation='relu',
            cell_type='LSTMCell',
            attention_layer=None
            # attention_layer=dict(
            #     type='GATLayer',
            #     attention_mechanism=dict(
            #         type='SingleLayerMechanism'
            #     ),
            #     activation='sigmoid'
            # )
        )
    ),
    loss_cls=dict(
        type='BinaryCrossEntropyLoss',
        loss_weight=1.0),
    accuracy_cls=dict(
        type='F1Score',
        num_classes=num_classes,
        average='micro',
        threshold=0.5
    )
)
# model training and testing settings
train_cfg = dict(
    reg_loss=dict(
        type='l2_loss',
        weight_decay=0.0005),
    )
test_cfg = dict(
    aggregator_activation='relu')

dataset_type = 'PPIDataset'
data_root = '/home/firiuza/MachineLearning/ppi/'
data = dict(
    train=dict(
        type=dataset_type,
        dataset_name='ppi',
        ann_file=data_root + 'train_ppi.pickle',
        depth=depth,
        nrof_neigh_per_batch=nrof_neigh_per_batch
    ),
    valid=dict(
        type=dataset_type,
        dataset_name='ppi',
        ann_file=data_root + 'valid_ppi.pickle'),
    test=dict(
        type=dataset_type,
        dataset_name='ppi',
        ann_file=data_root + 'test_ppi.pickle')
    )

# dataset settings
data_loader_type = 'TensorSlicesDataset'
data_loader_chain_rule = {
    'map': {'num_parallel_calls': 4},
    'batch': {'batch_size': 2},
}
data_loader = dict(
        train=dict(
            type=data_loader_type,
            ops_chain=data_loader_chain_rule,
            map_func_name='prepare_train_data'
        )
)
# learning policy
lr_schedule = dict(
    initial_learning_rate=5e-4,
    decay_steps=1000,
    decay_rate=0.99,
    staircase=True)
# optimizer
optimizer = dict(
    type='GraphSAGEOptimizer',
    optimizer_cfg=dict(
        type='Adam',
        params=None,
        lr_schedule_type='ExponentialDecay',
        lr_schedule=lr_schedule)
)

use_TensorBoard=True

# yapf:enable
# runtime settings
total_epochs = 500

log_level = 'INFO'
work_dir = '/home/firiuza/PycharmProjects/GraphSAGE/run_models/run_ppi_%s_%s' % (model['custom_aggregator']['aggregator_type']['type'],
                                                                             datetime.strftime(datetime.now(), '%Y%m%d-%H%M%S'))

restore_model_path = None

workflow = [('train', 1), ('valid', 1)]
